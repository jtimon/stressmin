stressmin
=========

Stress http rest servers

Install:

make

Shell:

make shell

Examples:

./.pyenv/bin/python ./bin/stress.py --url=https://www.google.com

./.pyenv/bin/python ./bin/stress.py --url=http://127.0.0.1:8100/api/v1/asset -t 10 -p 10

./.pyenv/bin/python ./bin/stress.py --url=http://127.0.0.1:8332 --action=post --auth=user:password --data='{"method":"getinfo"}'

