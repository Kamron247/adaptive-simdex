
Static Limits:
```
python ./main.py --config ./experiments/user_experience.yaml --refs ../data/release01-2021-12-29/ref-solutions.csv ../data/release01-2021-12-29/data.csv.gz
```

Hueristic Experiment:

```
python ./main.py --config ./experiments/user_experience_adaptive_limits.yaml --refs ../data/release01-2021-12-29/ref-solutions.csv ../data/release01-2021-12-29/data.csv.gz
```

Control Theory Experiment: 
```
python ./main.py --config ./experiments/user_experience_adaptive_control_limits.yaml --refs ../data/release01-2021-12-29/ref-solutions.csv ../data/release01-2021-12-29/data.csv.gz
```

Reinforcement Learning Experiment:
```
python ./main.py --config ./experiments/user_experience_rl_adaptive_limits_demo.yaml --refs ../data/release01-2021-12-29/ref-solutions.csv ../data/release01-2021-12-29/data.csv.gz
```


