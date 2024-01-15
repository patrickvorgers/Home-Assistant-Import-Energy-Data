/* After importing the new and old CSV files they can be compared using the below statements */
/* To be sure you have to check both ways new/old and old/new                                */

SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM gas_data_old_statistics_short_term;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t1_data_old_statistics_short_term;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_in_t2_data_old_statistics_short_term;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t1_data_old_statistics_short_term;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM feed_out_t2_data_old_statistics_short_term;


SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_old_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_new_statistics;

SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_new_statistics
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_old_statistics;


SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_old_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_new_statistics_short_term;

SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_new_statistics_short_term
EXCEPT
SELECT state, sum, metadata_id, created_ts, start_ts FROM solar_data_old_statistics_short_term;