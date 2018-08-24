CREATE EXTERNAL TABLE `elb_logs`(
  `request_timestamp` string COMMENT '',
  `elb_name` string COMMENT '',
  `request_ip` string COMMENT '',
  `request_port` int COMMENT '',
  `backend_ip` string COMMENT '',
  `backend_port` int COMMENT '',
  `request_processing_time` double COMMENT '',
  `backend_processing_time` double COMMENT '',
  `client_response_time` double COMMENT '',
  `elb_response_code` string COMMENT '',
  `backend_response_code` string COMMENT '',
  `received_bytes` bigint COMMENT '',
  `sent_bytes` bigint COMMENT '',
  `request_verb` string COMMENT '',
  `url` string COMMENT '',
  `protocol` string COMMENT '',
  `user_agent` string COMMENT '',
  `ssl_cipher` string COMMENT '',
  `ssl_protocol` string COMMENT '')
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'input.regex'='([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*):([0-9]*) ([.0-9]*) ([.0-9]*) ([.0-9]*) (-|[0-9]*) (-|[0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" (\"[^\"]*\") ([A-Z0-9-]+) ([A-Za-z0-9.-]*)$')
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://athena-examples-us-west-2/elb/plaintext'
TBLPROPERTIES (
  'transient_lastDdlTime'='1528512629')