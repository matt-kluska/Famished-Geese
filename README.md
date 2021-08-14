# Famished-Geese
If download kaggle_environments and encountering a gfootball error from delete the football environment from your kaggle_environments install location.





## Double Deep Q-Network

Written in pytorch can be found in the DDQN folder. 
```
module unload pytorch python3
module load python3/3.8.6 pytorch/1.8.1
source geese-torch-env/bin/activate
```
Note: order matters with the above commands

## Deep Q-Network

Written in tensorflow with tf-agents can be found in tf-agents folder

```
module unload tensorflow python3
module load python3/3.8.10 tensorflow/2.5.0
source geese-tf-env/bin/activate
```
Note: order matters with the above commands

Objectives:
Training:
Run Train.py to start training the agent. 
Checkpointing:
Train.py creates a variable for a checkpoint directory that can be either restored or initialized. 
Logging and visualizations:
You can view existing logs from the commandline by typing:

'''
Tensorboard --logdir logs-big
'''

This will open up a web page in your browser and allow you to review past tensorboard events as well as stream the results of current training runs.

Link to google slides

https://docs.google.com/presentation/d/1FcyikhtENs2Bqo-xRVE65cZJX57OnCBr/edit?usp=sharing&ouid=113817137264964264363&rtpof=true&sd=true
