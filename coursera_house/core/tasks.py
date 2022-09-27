from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mail
#from coursera_house.celery import task
from coursera_house.core.views import *
from coursera_house.core.models import Setting
from coursera_house.settings import *

#import schedule
#import time

#@task()
def smart_home_manager():
    """
    Опрашиваю сервер, сравниваю значения с теми, которые мне нужны
    Если надо, то выполняю пост запрос, чтобы изменить на сервере температуру
    """
    # receive actual data from server
    try:
        response = requests.get(SMART_HOME_API_URL,
                                headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'})
    except:
        return HttpResponse(status=502)

    if response.ok:
        response_json_data = json.loads(response.text)['data']
    else:
        return HttpResponse(status=502) #response.status_code)


    actual_sensor_info = {}
    for sensor_data in response_json_data:
        actual_sensor_info[sensor_data['name']] = sensor_data['value']

    # receive db-stored values (desired temperatures)
    desired_bedroom_temp = Setting.objects.get(controller_name='bedroom_target_temperature').value
    desired_boiler_temp = Setting.objects.get(controller_name='hot_water_target_temperature').value

    #print(f'temperatures: {desired_bedroom_temp}, {desired_boiler_temp}')

    #different checks
    changes_dict_list = []
    devices_to_turn_off = []
    devices_to_turn_on = []

    is_leak = (actual_sensor_info['leak_detector'] == True)
    is_cold_water_closed = (actual_sensor_info['cold_water'] == False)
    is_smoke = (actual_sensor_info['smoke_detector'] == True)

    #print(f"Boiler temp:{actual_sensor_info['boiler_temperature']}, {type(actual_sensor_info['boiler_temperature'])}")
    #print(f'{type(desired_boiler_temp)}')

    if is_leak:
        devices_to_turn_off.extend(['cold_water', 'hot_water'])
        send_mail('Attention: Leak occurred', 'Leak is detected. React urgently.',
                  EMAIL_HOST_USER, [EMAIL_RECEPIENT])
        is_cold_water_closed = True
    if is_cold_water_closed:
        devices_to_turn_off.extend(['boiler', 'washing_machine'])
    # Hot water conditions (boiler_temperature should be not None)
    if actual_sensor_info['boiler_temperature'] and not is_cold_water_closed:
        if actual_sensor_info['boiler_temperature'] < desired_boiler_temp*0.9:
            devices_to_turn_on.append('boiler')
        if actual_sensor_info['boiler_temperature'] > desired_boiler_temp*1.1:
            devices_to_turn_off.append('boiler')
    # Bedroom temperature conditions
    if actual_sensor_info['bedroom_temperature'] > desired_bedroom_temp*1.1:
        devices_to_turn_on.append('air_conditioner')
    if actual_sensor_info['bedroom_temperature'] < desired_bedroom_temp*0.9:
        devices_to_turn_off.append('air_conditioner')
    # Smoke detector
    if is_smoke:
        devices_to_turn_off.extend(['air_conditioner', 'bedroom_light', 'bathroom_light',
                                    'boiler', 'washing_machine'])
    # Curtains conditions
    if actual_sensor_info['curtains'] != 'slightly_open':
        if (actual_sensor_info['outdoor_light'] > 50) or (actual_sensor_info['bedroom_light'] == True):
            devices_to_turn_off.append('curtains')
        elif (actual_sensor_info['outdoor_light'] < 50) and (actual_sensor_info['bedroom_light'] == False):
            devices_to_turn_on.append('curtains')
        elif (actual_sensor_info['outdoor_light'] > 50) and is_smoke:
            devices_to_turn_on.append('curtains')

    devices_to_turn_on = [x for x in devices_to_turn_on if x not in devices_to_turn_off]


    for device in set(devices_to_turn_on):
        if actual_sensor_info[device] not in (True, 'open', 'on', 'broken'):
            if device == 'curtains':
                changes_dict_list.append({'name': device,
                                          'value': 'open'})
            elif device == 'washing_machine':
                changes_dict_list.append({'name': device,
                                          'value': 'on'})
            else:
                changes_dict_list.append({'name': device,
                                          'value': True})

    for device in set(devices_to_turn_off):
        # if device == 'washing_machine':
        #     print(f'Washing machine: {actual_sensor_info[device]}, {type(actual_sensor_info[device])}' )
        #     print(actual_sensor_info[device] == 'off')
        #     print(actual_sensor_info[device] not in (False, 'close', 'off', 'broken'))

        if actual_sensor_info[device] not in (False, 'close', 'off', 'broken'):
            if device == 'curtains':
                changes_dict_list.append({'name': device,
                                          'value': 'close'})
            elif device == 'washing_machine':
                changes_dict_list.append({'name': device,
                                          'value': 'off'})
            else:
                changes_dict_list.append({'name': device,
                                          'value': False})

    if len(changes_dict_list) > 0:
        # print(f'actual {actual_sensor_info}')
        # print()
        # print(f'To change {changes_dict_list}')
        # print()
        # print()
        requests.post(SMART_HOME_API_URL, headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'},
                      data=json.dumps({'controllers': changes_dict_list}))


