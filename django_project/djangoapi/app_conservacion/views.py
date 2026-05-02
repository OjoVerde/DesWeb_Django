import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from scripts.crud_zonas_conservacion import ZonaConservacionCRUD
from scripts.crud_red_canales import RedCanalCRUD
from scripts.crud_estaciones_monitoreo import EstacionMonitoreoCRUD


def _parse_request_body(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}


def _convert_tuple_geom_to_wkt(data):
    if not data or not data.get('data'):
        return data
    converted_data = []
    for row in data['data']:
        new_row = []
        for item in row:
            if hasattr(item, 'wkt'):
                new_row.append(item.wkt)
            else:
                new_row.append(item)
        converted_data.append(new_row)
    return {'ok': data['ok'], 'message': data['message'], 'data': converted_data}


@method_decorator(csrf_exempt, name='dispatch')
class ZonaConservacionView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = ZonaConservacionCRUD()

    def get(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        format_type = request.GET.get('format', 'dict')
        record_id = request.GET.get('id')

        query_data = {}
        if record_id:
            try:
                query_data['id'] = int(record_id)
            except ValueError:
                return JsonResponse(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero.", "data": None},
                    status=400
                )

        if format_type == 'tuple':
            result = self.crud.selectAsTuples(query_data if query_data else None)
            result = _convert_tuple_geom_to_wkt(result)
        else:
            result = self.crud.selectAsDicts(query_data if query_data else None)

        status = 200 if result.get('ok') else 500
        return JsonResponse(result, status=status)

    def post(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.insert(data)
        status = 201 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def put(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.update(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def delete(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.delete(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class RedCanalView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = RedCanalCRUD()

    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'dict')
        record_id = request.GET.get('id')

        query_data = {}
        if record_id:
            try:
                query_data['id'] = int(record_id)
            except ValueError:
                return JsonResponse(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero.", "data": None},
                    status=400
                )

        if format_type == 'tuple':
            result = self.crud.selectAsTuples(query_data if query_data else None)
            result = _convert_tuple_geom_to_wkt(result)
        else:
            result = self.crud.selectAsDicts(query_data if query_data else None)

        status = 200 if result.get('ok') else 500
        return JsonResponse(result, status=status)

    def post(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.insert(data)
        status = 201 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def put(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.update(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def delete(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.delete(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class EstacionMonitoreoView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = EstacionMonitoreoCRUD()

    def get(self, request, *args, **kwargs):
        format_type = request.GET.get('format', 'dict')
        record_id = request.GET.get('id')

        query_data = {}
        if record_id:
            try:
                query_data['id'] = int(record_id)
            except ValueError:
                return JsonResponse(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero.", "data": None},
                    status=400
                )

        if format_type == 'tuple':
            result = self.crud.selectAsTuples(query_data if query_data else None)
            result = _convert_tuple_geom_to_wkt(result)
        else:
            result = self.crud.selectAsDicts(query_data if query_data else None)

        status = 200 if result.get('ok') else 500
        return JsonResponse(result, status=status)

    def post(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.insert(data)
        status = 201 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def put(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.update(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)

    def delete(self, request, *args, **kwargs):
        data = _parse_request_body(request)
        result = self.crud.delete(data)
        status = 200 if result.get('ok') else 400
        return JsonResponse(result, status=status)