/* Copy statistics data (old) into separate tables so that they can be exported as CSV files - Change the ID's as needed */

CREATE TABLE gas_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 6;
CREATE TABLE gas_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 6;

CREATE TABLE feed_in_t1_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 7;
CREATE TABLE feed_in_t1_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 7;

CREATE TABLE feed_in_t2_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 8;
CREATE TABLE feed_in_t2_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 8;

CREATE TABLE feed_out_t1_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 9;
CREATE TABLE feed_out_t1_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 9;

CREATE TABLE feed_out_t2_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 10;
CREATE TABLE feed_out_t2_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 10;

CREATE TABLE solar_data_old_statistics AS SELECT * from statistics WHERE metadata_id = 352;
CREATE TABLE solar_data_old_statistics_short_term AS SELECT * from statistics_short_term WHERE metadata_id = 352;
