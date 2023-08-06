from django.db import models
import simplejson
import redis
from django.conf import settings

# Create your models here.
ACTIONS = (
    ('launch_cloudforms_vmachine', 'launch_cloudforms_vmachine'),
    ('destroy_cloudforms_vmachine', 'destroy_cloudforms_vmachine'),
    )
class ScaleAction(models.Model):
    name = models.CharField(max_length=100)
    action = models.CharField(max_length=100, choices=ACTIONS)
    scale_by = models.IntegerField() #2 will scale up by two. -2 will scale down by 2
    
    def __unicode__(self):
        return u"%s" % self.name
    
    def to_dict(self):
        return {"name": self.name,
             "scale_by": self.scale_by,}            
        
    def to_redis(self, justification):
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        data = self.to_dict()
        data["justificaction"] = justification
        r.lpush(settings.REDIS_ACTION_LIST, simplejson.dumps(data))
        
    @staticmethod
    def from_redis(data):        
        data = simplejson.loads(data)
        return ScaleAction(name=data["name"], scale_by=["scale_by"])
   
METRICS = (
    ("cpu_usage_snmp", "cpu_usage_snmp"),
    ("redis_list_length", 'redis_list_length'),
    ("http_response_time", "http_response_time"),
    )

   
OPERANDS = (
    ('>', '>'),
    ('<','<'),
    ('=', '='),
    ('<=', '<='),
    ('>=', '>='),    
    )

class Threshold(models.Model):
    assesment = models.CharField(max_length=300)
    time_limit = models.IntegerField() #seconds the threshold must be overtaken before it becomes an alarm
    metric = models.CharField(max_length=100, choices=METRICS) #metric that is going to be monitored. It'll be a mapping.
    operand = models.CharField(max_length=10, choices=OPERANDS)
    value = models.IntegerField() # the value of the threshold
    
    def __unicode__(self):
        return u"%s" % self.assesment
    
            
class MonitoredService(models.Model):
    name = models.CharField(max_length=300)
    threshold = models.ForeignKey(Threshold)
    action = models.ForeignKey(ScaleAction)
    active = models.BooleanField(default=True)
    """
    depending on the metric that the monitored service is about, you find here 
    the needed data for that metric
    """
    data = models.TextField() 
     
    def to_pypelib(self, ):        
        return "if %s %s %s then accept" % (
                self.threshold.metric, 
                self.threshold.operand, 
                self.threshold.value)     
    
    def __unicode__(self):
        return u"%s [%s], action %s" % (self.name, self.threshold, self.action)

    
class AlarmIndicator(models.Model):
    service = models.ForeignKey(MonitoredService, related_name='alarm_indicators')
    timestamp = models.DateTimeField(auto_now_add=True)
    