pytstatsd-collect
=================
简介
====
collect_pystatsd.py 利用 Statsd 将采集的数据发送给 pystatsd-server, 再由server转发给graphite,
采集的数据目前支持
nginx 的访问状态,包括: 5XX, 4XX, 3XX, 2XX, 采集状态根据nginx的日志格式来区分
fpm 的慢日志, 根据时间戳来计数
fpm 的错误日志, 根据时间戳来计数

配置
====
[common]
server=10.0.20.5                # pystatsd-server 所在ip
port=8125                       # pystatsd-server 监听端口(默认是8125)
local=10.0.20.7                 # 本机IP
interval=5                      # 采集频率

[nginx_access]
enable=1                        #是否采集nginx日志, 1 采集, 0 不采集
log_base=/home/www/logs         # nginx 日志所在目录
log_type=application.access.log # 各项目的 nginx 名字 

[fpm_slow]                      # 参考nginx 的配置,类似
enable=1
log_base=/home/www/logs
log_type=koubeirpc.log.slow

[fpm_error]
enable=1
log_base=/home/www/logs
log_type=koubeirpc.log.error

pytstatsd-server
================
pystatsd-server 帮助说明:

usage: pystatsd-server [-h] [-d] [-n NAME] [-p PORT] [-r TRANSPORT]
                       [--graphite-port GRAPHITE_PORT]
                       [--graphite-host GRAPHITE_HOST]
                       [--ganglia-port GANGLIA_PORT]
                       [--ganglia-host GANGLIA_HOST]
                       [--ganglia-spoof-host GANGLIA_SPOOF_HOST]
                       [--ganglia-gmetric-exec GMETRIC_EXEC]
                       [--ganglia-gmetric-options GMETRIC_OPTIONS]
                       [--flush-interval FLUSH_INTERVAL]
                       [--no-aggregate-counters]
                       [--counters-prefix COUNTERS_PREFIX]
                       [--timers-prefix TIMERS_PREFIX] [-t PCT] [-D]
                       [--pidfile PIDFILE] [--restart] [--stop]
                       [--expire EXPIRE]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           debug mode
  -n NAME, --name NAME  hostname to run on
  -p PORT, --port PORT  port to run on (default: 8125)
  -r TRANSPORT, --transport TRANSPORT
                        transport to use graphite, ganglia (uses embedded
                        library) or ganglia-gmetric (uses gmetric)
  --graphite-port GRAPHITE_PORT
                        port to connect to graphite on (default: 2003)
  --graphite-host GRAPHITE_HOST
                        host to connect to graphite on (default: localhost)
  --ganglia-port GANGLIA_PORT
                        Unicast port to connect to ganglia on
  --ganglia-host GANGLIA_HOST
                        Unicast host to connect to ganglia on
  --ganglia-spoof-host GANGLIA_SPOOF_HOST
                        host to report metrics as to ganglia
  --ganglia-gmetric-exec GMETRIC_EXEC
                        Use gmetric executable. Defaults to /usr/bin/gmetric
  --ganglia-gmetric-options GMETRIC_OPTIONS
                        Options to pass to gmetric. Defaults to -d 60
  --flush-interval FLUSH_INTERVAL
                        how often to send data to graphite in millis (default:
                        10000)
  --no-aggregate-counters
                        should statsd report counters as absolute instead of
                        count/sec
  --counters-prefix COUNTERS_PREFIX
                        prefix to append before sending counter data to
                        graphite (default: stats)
  --timers-prefix TIMERS_PREFIX
                        prefix to append before sending timing data to
                        graphite (default: stats.timers)
  -t PCT, --pct PCT     stats pct threshold (default: 90)
  -D, --daemon          daemonize
  --pidfile PIDFILE     pid file
  --restart             restart a running daemon
  --stop                stop a running daemon
  --expire EXPIRE       time-to-live for old stats (in secs)

example:
pystatsd-server -p 8125 --graphite-host 192.168.20.132 --graphite-port 2003 --counters-prefix system -d --flush-interval 1000

--graphite-host     为graphite的地址
--COUNTERS_PREFIX   作为发送到graphite的指定目录, 例如该案列指定到system目录, 不指定默认是statsd目录
--FLUSH_INTERVAL    指定发送数据到graphite的间隔, 毫秒为单位
