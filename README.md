# Auto-scaling-using-lambda-aws
## Requirements 
#### Bucket must be present and it has a pickle in it
##### and must have 2 alarms for ec2 instance one for when to scale up and other for when to scale down with naming alarm_for_scale_up and alarm_for_scale_down with one sns topic attached to lambda
###### replace path_to_pickle_file and bucket_name with yours
###### pickle must be a dictionary of tag,loadbalancer,ami,VolumeSize,instance_size,ami

###### tag is name which you represent your instance, loadbalancer to which your instance attach, VolumeSize is disk space 40 or 30, instance_size t2.mcrio or etc and ami image with instance should up.

###### example ex[tag]='test',ex['loadbalancer']='test',ex['VolumeSize']=30,ex['instance_size']='t2.micro',ex['ami']='id'
