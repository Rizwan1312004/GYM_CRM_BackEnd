import sys, os, traceback
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_management.settings')

try:
    import django
    django.setup()
    import gym.serializers
except BaseException as e:
    with open('error_dump.txt', 'w') as f:
        traceback.print_exc(file=f)
