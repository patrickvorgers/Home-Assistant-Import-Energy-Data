CREATE TABLE gas_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 6;
CREATE TABLE gas_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 6;

CREATE TABLE feed_in_t1_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 7;
CREATE TABLE feed_in_t1_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 7;

CREATE TABLE feed_in_t2_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 8;
CREATE TABLE feed_in_t2_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 8;

CREATE TABLE feed_out_t1_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 9;
CREATE TABLE feed_out_t1_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 9;

CREATE TABLE feed_out_t2_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 10;
CREATE TABLE feed_out_t2_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 10;

CREATE TABLE solar_data_new_statistics AS SELECT * from statistics WHERE metadata_id = 352;
CREATE TABLE solar_data_new_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 352;
