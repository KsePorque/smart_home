from django.urls import reverse_lazy
from django.views.generic import FormView
from django.http import HttpResponse
import requests
import json
from .models import Setting
from .form import ControllerForm
from coursera_house.settings import *

class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    db_values = {'bedroom_target_temperature': 21,
                'hot_water_target_temperature': 80,
                'bedroom_light': False,
                'bathroom_light': False}

    def set_changes(self, changes_dicts_list=[]):
        for changes_dict in changes_dicts_list:
            record = Setting.objects.get(controller_name=changes_dict['name'])
            record.value = changes_dict['value']
            record.save()
            self.db_values[changes_dict['name']] = changes_dict['value']

        #print(record.value)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if len(context.items()) == 0:
            return HttpResponse(status=502)
        else:
            return super(ControllerView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # to store in database
        bedroom_target_temperature_dict = {'name': 'bedroom_target_temperature',
                                           'value': request.POST.get('bedroom_target_temperature')}
        hot_water_target_temperature_dict = {'name': 'hot_water_target_temperature',
                                             'value': request.POST.get('hot_water_target_temperature')}

        self.set_changes([bedroom_target_temperature_dict, hot_water_target_temperature_dict])

        # to send to server
        bedroom_light_dict = {'name': 'bedroom_light',
                              'value': True if request.POST.get('bedroom_light')=='on' else False}
        bathroom_light_dict = {'name': 'bathroom_light',
                               'value': True if request.POST.get('bathroom_light')=='on' else False}

        changes_dict_list = [bedroom_light_dict, bathroom_light_dict]


        # cond1 = (16 <= int(bedroom_target_temperature_dict['value']) <= 50)
        # cond2 = (24 <= int(hot_water_target_temperature_dict['value']) <= 90)

        #self.form_valid(self.form_class)
        if self.form_valid(self.form_class):
        #if cond1 and cond2:
            #return self.form_valid(self.form_class)

            try:
                response = requests.post(SMART_HOME_API_URL, headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'},
                                        data=json.dumps({'controllers': changes_dict_list}))
            except:
                return HttpResponse(status=502)

            if response.ok:
                return self.form_valid(self.form_class) # super(ControllerView, self).post(request, *args, **kwargs)
            else:
                return HttpResponse(status=502)

        else:
           return super(ControllerView, self) #HttpResponse(status=400)


    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()

        try:
            response = requests.get(SMART_HOME_API_URL,
                                    headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'})
        except:
            return {} #HttpResponse(status=502)

        if response.ok:
            response_json_data = json.loads(response.text)
        else:
            return {} #HttpResponse(status=502)


        if 'data' in response_json_data.keys():
            response_json_data = response_json_data['data']
            sensor_info = {}
            for sensor_data in response_json_data:
                sensor_info[sensor_data['name']] = sensor_data['value']
                if sensor_data['name'] == 'bedroom_light':
                    self.db_values['bedroom_light'] = sensor_data['value']
                elif sensor_data['name'] == 'bathroom_light':
                    self.db_values['bathroom_light'] = sensor_data['value']

            context['data'] = sensor_info
        else:
            context = {}

        return context

    def get_initial(self):
        """ Вот тут последние данные из базы и актуальные значения для устройств"""
        try:
            response = requests.get(SMART_HOME_API_URL,
                                    headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'})
        except:
            return HttpResponse(status=502)

        if response.ok:
            context_data = json.loads(response.text)['data']
        else:
            return HttpResponse(status=502) #response.status_code)


        record_bedroom_temp = Setting.objects.get(controller_name='bedroom_target_temperature')
        record_boiler_temp = Setting.objects.get(controller_name='hot_water_target_temperature')
        self.db_values['bedroom_target_temperature'] = record_bedroom_temp.value
        self.db_values['hot_water_target_temperature'] = record_boiler_temp.value

        for data in context_data:
            if data['name'] == 'bedroom_light':
                self.db_values['bedroom_light'] = bool(data['value'])
            elif data['name'] == 'bathroom_light':
                self.db_values['bathroom_light'] = bool(data['value'])

        return self.db_values

    def form_valid(self, form):
        return super(ControllerView, self).form_valid(form)
