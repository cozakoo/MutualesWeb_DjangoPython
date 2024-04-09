from django.shortcuts import render

from django.views.generic import TemplateView
from datetime import datetime
from collections import Counter
from django.db.models import Count

class reporteMutualDeclaracionesJuradasView(TemplateView):
    template_name = 'reporte_mutuales_declaraciones.html'
    
    def get_graph_alquileres(self):

        pass

#         data_confirmados = Counter()
#         data_enCurso = Counter()
#         data_finalizados = Counter()
#         data_cancelados = Counter()

#         alquileres_por_mes = Alquiler.objects.all()
        
#         # Counting rentals for each month and state
#         for alquiler in alquileres_por_mes:
#             month = alquiler.fecha_alquiler.month
#             if alquiler.estado == 1:  # Confirmado
#                 data_confirmados[month] += 1
#             elif alquiler.estado == 2:  # Cancelado
#                 data_enCurso[month] += 1
#             elif alquiler.estado == 3:  # Cancelado
#                 data_finalizados[month] += 1
#             elif alquiler.estado == 4:  # Finalizado
#                 data_cancelados[month] += 1

#         # Converting the Counters to lists of counts for each month
#         data_confirmados_list = [data_confirmados[month] for month in range(1, 13)]
#         data_enCurso_list = [data_enCurso[month] for month in range(1, 13)]
#         data_finalizados_list = [data_finalizados[month] for month in range(1, 13)]
#         data_cancelados_list = [data_cancelados[month] for month in range(1, 13)]

#         # Defining categories for X-axis
#         categories = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
#         return data_confirmados_list, data_enCurso_list,  data_finalizados_list, data_cancelados_list, categories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'En construcción....'
        
        # Get the data and categories for the graph
        # data_confirmados_list, data_enCurso_list, data_finalizados_list, data_cancelados_list, categories = self.get_graph_alquileres()
        
        # Add the data and categories to the context
        context['graph_alquileres'] = {
            # 'data_confirmados_list': data_confirmados_list,
            # 'data_enCurso_list': data_enCurso_list,
            # 'data_finalizados_list': data_finalizados_list,
            # 'data_cancelados_list': data_cancelados_list,
            # 'categories': categories,
            'y_axis_title': 'Total de alquileres',  # Y-axis title
        }
        return context