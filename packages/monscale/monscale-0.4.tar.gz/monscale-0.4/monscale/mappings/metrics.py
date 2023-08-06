import logging, simplejson, redis
from snmp import get_variable

#logging.basicConfig(level=logging.DEBUG)
def load_data(data):
    return simplejson.loads(data)


def cpu_usage_snmp(ctxt):
    """
    ctxt["service"].data["host"]
    ctxt["service"].data["port"]
    ctxt["service"].data["snmp_read_comunity"]
    ctxt["service"].data["snmp_mib"]
    ctxt["service"].data["snmp_variable"]    
    """
    logging.debug("[metric: cpu_usage_snmp] Entering  ...")

    logging.debug("[metric: cpu_usage_snmp] metric ended")
    return 60
    
    
def redis_list_length(ctxt):
    """
    ctxt["service"].data["redis_host"]  #default: localhost
    ctxt["service"].data["redis_port"] #default: 6379
    ctxt["service"].data["redis_db"]  #default: 0
    ctxt["service"].data["redis_list_name"] 
    """
        
    try:
        print ctxt["service"].data
        data = simplejson.loads(ctxt["service"].data)
        r = redis.StrictRedis(
            host=data.get("redis_host", "localhost"), 
            port=data.get("redis_port", 6379), 
            db=data.get("redis_db", 0))
        list_length = r.llen(data["redis_list_name"])
    except Exception, er:
        logging.error("[metric: redis_list_length] Exception msg: %s" % er)
        return "[metric: redis_list_length] ERROR trying to rerieve the metric value"
    logging.debug("[metric: redis_list_length] current length: %d" % list_length)
    logging.debug("[metric: redis_list_length] metric ended")
    return list_length


def http_response_time(ctxt):
    pass


mappings = [
    cpu_usage_snmp,
    redis_list_length,
    http_response_time,
    ]