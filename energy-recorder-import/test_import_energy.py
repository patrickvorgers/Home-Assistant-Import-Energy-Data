"""Offline tests only: no network, no credentials, no live HA writes."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import import_energy as imp

B = 1704067200
META = {"statistics_unit_of_measurement": "kWh", "unit_class": "energy", "mean_type": 0,
        "name": "Meter", "source": "recorder", "has_sum": True}
CFG = {"statistic_id": "sensor.meter", "overlap_tolerance": 0.001}


def fixture():
    # Existing HA starts at hour 2. Source overlaps hours 2 and 3.
    readings = [(B, 100), (B+3600, 105), (B+7200, 110), (B+10800, 112), (B+14400, 115)]
    source, notes = imp.source_statistics(readings)
    old = [{"ts": B+7200, "state": 112, "sum": 2}, {"ts": B+10800, "state": 115, "sum": 5}]
    short = [{"ts": B+11100, "state": 115.5, "sum": 5.5},
             {"ts": B+11400, "state": 116, "sum": 6}]
    plan = imp.make_sensor_plan(CFG, META, source, old, short, B+14400, notes)
    return plan


class FakeHA:
    def __init__(self, plan):
        self.hour = copy.deepcopy(plan["before_hour"])
        self.short = copy.deepcopy(plan["before_5minute"])
        self.calls = []
        self.drop_adjustment_response = False
        self.fail_import = False
        self.suppress_adjustment = False

    def rows(self, sensor, start, end, period="hour"):
        source = self.hour if period == "hour" else self.short
        return sorted(copy.deepcopy([r for r in source if start <= r["ts"] < end]), key=lambda r:r['ts'])

    def call(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command == "recorder/import_statistics":
            if self.fail_import:
                raise OSError("network interrupted")
            for stat in kwargs["stats"]:
                ts = int(imp.datetime.fromisoformat(stat["start"]).timestamp())
                self.hour = [r for r in self.hour if r["ts"] != ts]
                self.hour.append({"ts": ts, "state": stat["state"], "sum": stat["sum"]})
        elif command == "recorder/adjust_sum_statistics":
            start = int(imp.datetime.fromisoformat(kwargs['start_time']).timestamp())
            if not self.suppress_adjustment:
                for table in (self.hour, self.short):
                    for row in table:
                        if row['ts'] >= start:
                            row['sum'] += kwargs['adjustment']
            if self.drop_adjustment_response:
                raise OSError("response lost after commit")
        else:
            raise AssertionError(command)


class ImportTests(unittest.TestCase):
    def test_prepend_calculates_sum_from_increments_not_meter_baseline(self):
        plan = fixture()
        self.assertEqual([r['sum'] for r in plan['historical']], [5, 10])
        self.assertEqual(plan['correction'], 10)
        self.assertEqual(plan['overlap_hours'], 2)

    def test_existing_sum_baseline_is_aligned_not_blindly_increased(self):
        plan = fixture()
        source, notes = imp.source_statistics([(B,100),(B+3600,105),(B+7200,110),(B+10800,112),(B+14400,115)])
        old = [{**r, 'sum':r['sum']+100} for r in plan['before_hour']]
        result = imp.make_sensor_plan(CFG,META,source,old,plan['before_5minute'],plan['end'],notes)
        self.assertEqual(result['correction'], -90)

    def test_overlap_mismatch_refuses_plan(self):
        plan = fixture()
        source, notes = imp.source_statistics([(B,100),(B+3600,105),(B+7200,110),(B+10800,112),(B+14400,116)])
        with self.assertRaisesRegex(ValueError, 'Overlap consumption differs'):
            imp.make_sensor_plan(CFG,META,source,plan['before_hour'],plan['before_5minute'],plan['end'],notes)

    def test_no_overlap_refuses_plan(self):
        plan = fixture()
        with self.assertRaisesRegex(ValueError, 'overlapping hours'):
            imp.make_sensor_plan(CFG,META,plan['historical'],plan['before_hour'],plan['before_5minute'],plan['end'],{})

    def test_counter_reset_requires_explicit_policy(self):
        with self.assertRaisesRegex(ValueError, 'Counter decrease'):
            imp.source_statistics([(B,100),(B+3600,5),(B+7200,8)])
        rows, notes = imp.source_statistics([(B,100),(B+3600,5),(B+7200,8)],reset_policy='zero')
        self.assertEqual([r['sum'] for r in rows],[5,8])
        self.assertEqual(notes['assumed_zero_resets'],1)

    def test_coarse_data_requires_explicit_distribution(self):
        with self.assertRaisesRegex(ValueError,'Missing hourly boundaries'):
            imp.source_statistics([(B,100),(B+86400,124),(B+172800,148)])
        rows,notes=imp.source_statistics([(B,100),(B+86400,124),(B+172800,148)],gap_policy='uniform')
        self.assertEqual(len(rows),48)
        self.assertEqual(rows[-1]['sum'],48)
        self.assertEqual(notes['estimated_hours'],48)

    def test_source_units(self):
        self.assertEqual(imp.unit_factor('Wh','kWh'),0.001)
        self.assertEqual(imp.unit_factor('m³','L'),1000)
        with self.assertRaises(ValueError):imp.unit_factor('Wh','m³')

    def test_low_high_precedence_duplicate_and_invalid_values(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root=Path(folder)
            (root/'gas_low_resolution.csv').write_text(f'{B},100\n{B+3600},101\n{B+7200},999\n')
            (root/'gas_high_resolution.csv').write_text(f'{B+3600},102\n{B+7200},103\n')
            config={'import_name':'gas','source_unit':'m³','files':['gas_low_resolution.csv','gas_high_resolution.csv']}
            rows,_=imp.read_source(config,root,'m³')
            self.assertEqual(rows,[(B,100),(B+3600,102),(B+7200,103)])
            (root/'gas_high_resolution.csv').write_text(f'{B+3600},102\n{B+3600},104\n')
            with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):imp.read_source(config,root,'m³')
            (root/'gas_high_resolution.csv').write_text(f'{B+3600},nan\n')
            with self.assertRaisesRegex(ValueError,'NaN'):imp.read_source(config,root,'m³')

    def test_terminal_boundary_is_not_imported_as_fake_zero(self):
        rows,_=imp.source_statistics([(B,100),(B+3600,105),(B+7200,110)])
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[-1]['state'],110)

    def test_apply_preserves_states_and_shifts_both_tables(self):
        plan=fixture(); client=FakeHA(plan); state={}
        imp.apply_sensor(client,plan,state,lambda:None,batch_size=1)
        self.assertEqual(state['phase'],'complete')
        self.assertEqual([r['sum'] for r in client.rows(plan,B,B+14400)], [5,10,12,15])
        self.assertEqual([r['state'] for r in client.rows(plan,B+7200,B+14400)],[112,115])
        self.assertEqual([r['sum'] for r in client.short],[15.5,16])
        count=len(client.calls)
        imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(len(client.calls),count)

    def test_resume_partial_import(self):
        plan=fixture(); client=FakeHA(plan); state={'phase':'importing'}
        client.hour.append(copy.deepcopy(plan['historical'][0]))
        imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(state['phase'],'complete')
        self.assertEqual(len(client.hour),4)

    def test_lost_adjustment_response_does_not_double_adjust_on_resume(self):
        plan=fixture(); client=FakeHA(plan); state={}; client.drop_adjustment_response=True
        with self.assertRaises(OSError):imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(state['phase'],'adjusting')
        client.drop_adjustment_response=False
        imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(sum(cmd=='recorder/adjust_sum_statistics' for cmd,_ in client.calls),1)
        self.assertEqual(state['phase'],'complete')

    def test_unknown_adjustment_status_never_replays_command(self):
        plan=fixture(); client=FakeHA(plan); state={'phase':'adjusting'}
        def check_once(check,*args,**kwargs):
            if not check():raise RuntimeError('unconfirmed')
        with patch.object(imp,'wait_for',check_once):
            with self.assertRaisesRegex(RuntimeError,'unconfirmed'):
                imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(client.calls,[])

    def test_destination_changed_after_preview_is_rejected(self):
        plan=fixture(); client=FakeHA(plan); client.hour[-1]['sum']+=1
        with self.assertRaisesRegex(RuntimeError,'changed since planning'):
            imp.apply_sensor(client,plan,{},lambda:None)
        self.assertEqual(client.calls,[])

    def test_conflicting_partial_import_is_rejected(self):
        plan=fixture(); client=FakeHA(plan); client.hour.append({**plan['historical'][0],'sum':500})
        with self.assertRaisesRegex(RuntimeError,'conflicting partial'):
            imp.apply_sensor(client,plan,{'phase':'importing'},lambda:None)

    def test_readback_failure_does_not_report_complete(self):
        plan=fixture(); client=FakeHA(plan); state={}; client.suppress_adjustment=True
        def check_once(check,*args,**kwargs):
            if not check():raise RuntimeError('unconfirmed')
        with patch.object(imp,'wait_for',check_once):
            with self.assertRaisesRegex(RuntimeError,'unconfirmed'):
                imp.apply_sensor(client,plan,state,lambda:None)
        self.assertEqual(state['phase'],'adjusting')

    def test_websocket_milliseconds_and_unit_override(self):
        client=object.__new__(imp.HAClient); calls=[]
        def call(cmd,**kw):
            calls.append(kw)
            return {'sensor.meter':[{'start':B*1000,'sum':10,'state':110}]}
        client.call=call
        rows=client.rows({'statistic_id':'sensor.meter','unit_class':'energy','unit':'kWh'},B,B+3600)
        self.assertEqual(rows,[{'ts':B,'sum':10,'state':110}])
        self.assertEqual(calls[0]['units'],{'energy':'kWh'})

    def test_complete_preview_and_apply_workflow_and_journal(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root=Path(folder)
            csv_path=root/'elec_high_resolution.csv'
            csv_path.write_text('\n'.join(f'{B+i*3600},{value*1000}' for i,value in
                                        enumerate([100,105,110,112,115]))+'\n')
            config_path=root/'config.json'
            config_path.write_text(json.dumps({'sensors':[{
                **CFG,'import_name':'elec','source_unit':'Wh','files':[csv_path.name]}]}))
            client=FakeHA(fixture()); client.url='http://ha.test'; client.version='2026.10.1'
            client.metadata=lambda:{'sensor.meter':META}
            with patch.object(imp.time,'time',return_value=B+21600):
                plan=imp.build_plan(client,config_path)
                self.assertEqual(client.calls,[], 'Preview must never write to Home Assistant')
                plan_path=root/'plan.json'
                imp.save_json(plan_path,plan)
                imp.apply_plan(client,plan_path)
                journal=json.loads((root/'plan.json.journal.json').read_text())
                self.assertEqual(journal['sensors']['sensor.meter']['phase'],'complete')
                count=len(client.calls)
                imp.apply_plan(client,plan_path)
                self.assertEqual(len(client.calls),count)
                self.assertFalse((root/'plan.json.lock').exists())

    def test_metadata_and_plan_destination_guard(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            sensor=fixture()
            plan={'format':1,'created':int(imp.time.time()),'ha_version':'2026.10.1',
                  'ha_url':'http://ha.test','sensors':[sensor],'plan_id':imp.digest([sensor])}
            path=Path(folder)/'plan.json';imp.save_json(path,plan)
            client=FakeHA(sensor);client.version='2026.10.1';client.url='http://other.test'
            with self.assertRaisesRegex(ValueError,'URL differs'):imp.apply_plan(client,path)
            client.url='http://ha.test'
            client.metadata=lambda:{'sensor.meter':{**META,'statistics_unit_of_measurement':'Wh'}}
            with self.assertRaisesRegex(ValueError,'metadata changed'):imp.apply_plan(client,path)
            self.assertEqual(client.calls,[])

    def test_nullable_states_are_preserved_and_unknown_phase_is_rejected(self):
        self.assertTrue(imp.rows_match([{'ts':B,'sum':1,'state':None}],
                                     [{'ts':B,'sum':1,'state':None}],0.01,True))
        plan=fixture();client=FakeHA(plan)
        with self.assertRaisesRegex(ValueError,'Unknown journal phase'):
            imp.apply_sensor(client,plan,{'phase':'unknown'},lambda:None)
        self.assertEqual(client.calls,[])


if __name__=='__main__':unittest.main()
