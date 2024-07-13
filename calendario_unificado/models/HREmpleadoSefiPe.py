# -*- coding: utf-8 -*-
from odoo import fields, models, api

import datetime
import random
import string
from copy import copy

import logging

_logger = logging.getLogger(__name__)


class HREmpleadoSefiPe(models.Model):
    _inherit = 'hr.employee'
    _description = 'Empleado de proyectos especiales'

    # presencialidad_id = fields.One2many('hr.sefip e.presencialidad', 'employee_id', string='Presencialidad',limit=1)

    lunes = fields.Selection(string='Lunes', selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                             required=False, default='presencial')
    martes = fields.Selection(string='Martes', selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                              required=False, default='presencial')
    miercoles = fields.Selection(string='Miercoles', selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                                 required=False, default='presencial')
    jueves = fields.Selection(string='Jueves', selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                              required=False, default='presencial')
    viernes = fields.Selection(string='Viernes', selection=[('presencial', 'Presencial'), ('remoto', 'Remoto')],
                               required=False, default='presencial')

    @api.model
    def create(self, vals):
        employee = super(HREmpleadoSefiPe, self).create(vals)
        # Crear un usuario para el nuevo empleado
        user_vals = {
            'name': employee.name,
            'login': self._generate_username(employee),
            'password': self._generate_password(),
            # Otros campos del usuario que necesites establecer
        }

        if vals.get('birthday'):
            year = fields.Date.context_today(self).year
            birthday = fields.Date.from_string(vals.get('birthday')).replace(year=year)
            self.env['hr.calendario_unificado'].create({
                'id_father': employee.id,
                'name': 'Cumple:' + employee.name,
                'date_from': birthday,
                'date_to': birthday,
                'descripcion': 'Cumpleaños del colaborador',
                'tipo_evento': 'cumple'
            })

        user = self.env['res.users'].create(user_vals)

        employee.user_id = user
        self.editar_tarea(employee, user)
        return employee

    def _generate_username(self, employee):
        # Generar un nombre de usuario basado en el nombre y apellido del empleado
        split = employee.name.split(' ')
        username = (split[0] + '.' + split[1]).lower()
        # Verificar si el nombre de usuario ya existe y agregar un sufijo si es necesario
        existing_users = self.env['res.users'].search([('login', '=', username)])
        if existing_users:
            username += str(len(existing_users))
        return username

    def _generate_password(self):
        # Generar una contraseña aleatoria
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def editar_tarea(self, employee, user):

        fecha_con_hora = self.agergar_tiempo_fecha(fields.Date.context_today(self))

        if self.fecha_laboorable(fields.Date.context_today(self)):

            fecha_lunes, fecha_viernes = self.obtener_lunes_y_viernes()

            project = self.env['project.project'].search([('name', '=', 'Presencialidad')], limit=1)

            task_list = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('date_deadline', '>=', fecha_lunes),
                ('date_deadline', '<=', fecha_viernes)
            ])
            if len(task_list) > 0:
                task_list_ordenada = sorted(task_list, key=lambda x: x.id)
                task_list_presencial = task_list_ordenada[:5]
                task_list_remoto = task_list_ordenada[5:]
                nombres_dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes"]

                # edito las tareas presencial y remoto en le caso que corresponda
                for index, dia in enumerate(nombres_dias_semana):
                    modalidad = getattr(employee, dia)
                    if modalidad == 'presencial':
                        task_presencial = task_list_presencial[index]
                        task_presencial.cantidad_personas_tarea += 1
                        task_presencial.name = 'Presencial:' + str(task_presencial.cantidad_personas_tarea)
                        array_auxiliar = copy(task_presencial.user_ids.ids)
                        array_auxiliar.append(user.id)
                        task_presencial.write({
                            'cantidad_personas_tarea': task_presencial.cantidad_personas_tarea,
                            'name': task_presencial.name,
                            'user_ids': [(6, 0, array_auxiliar)],
                        })
                    else:
                        task_remoto = task_list_remoto[index]
                        task_remoto.cantidad_personas_tarea += 1
                        task_remoto.name = 'Remoto:' + str(task_remoto.cantidad_personas_tarea)
                        array_auxiliar = copy(task_remoto.user_ids.ids)
                        array_auxiliar.append(user.id)
                        task_remoto.write({
                            'cantidad_personas_tarea': task_remoto.cantidad_personas_tarea,
                            'name': task_remoto.name,
                            'user_ids': [(6, 0, array_auxiliar)],
                        })

    def agergar_tiempo_fecha(self, fecha):
        time_8_am = datetime.time(8, 0, 0)
        # fecha = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').date()
        fecha = fields.Date.from_string(fecha)
        fecha_con_hora = datetime.datetime.combine(fecha, time_8_am)
        return fecha_con_hora

    def fecha_laboorable(self, fecha):
        if datetime.datetime.strptime(str(fecha), '%Y-%m-%d').weekday() > 4:
            return False
        else:
            return True

    def obtener_lunes_y_viernes(self):
        # Obtener la fecha actual
        hoy = fields.Date.context_today(self)

        # Convertir la fecha actual a objeto datetime
        # fecha_actual = datetime.datetime.strptime(str(hoy), '%Y-%m-%d')
        fecha_actual = fields.Datetime.from_string(hoy)

        # Obtener el día de la semana (lunes = 0, martes = 1, ..., domingo = 6)
        dia_semana = fecha_actual.weekday()

        # Calcular la diferencia de días necesaria para llegar al lunes
        diferencia_lunes = datetime.timedelta(days=dia_semana)

        # Calcular la fecha del lunes
        lunes = fecha_actual - diferencia_lunes

        # Calcular la fecha del viernes (5 días después del lunes)
        viernes = lunes + datetime.timedelta(days=5)

        return lunes, viernes

