import pytz
import time
import math
import datetime
from dateutil import parser, rrule
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
from datetime import date, timedelta
from odoo import fields, models, api, _
from odoo.report import render_report
from odoo.exceptions import Warning, ValidationError, UserError
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from urlparse import urljoin
from lxml import etree
from odoo.osv.orm import setup_modifiers

class holiday_group_config_line_inherit(models.Model):
    _inherit = 'holiday.group.config.line'  

    @api.multi               
    def leave_request_reminder_notification(self):
        approvers = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        params = {}
        redirect_url = '/web#view_type=list&model=hr.holidays&menu_id=%(menu_id)d&action=%(action_id)d'
        ir_model_obj = self.env['ir.model.data']
        menu_model,menu_id = ir_model_obj.sudo().get_object_reference('hr_holidays', 'menu_hr_holidays_root')
        submenu_model,sub_menu_id = ir_model_obj.sudo().get_object_reference('hr_holidays', 'menu_open_department_leave_approve')
        leave_link = ""
        if menu_id:
            params['menu_id'] = menu_id
            menu = self.env['ir.ui.menu'].sudo().search([("id","=",sub_menu_id)])
            params['action_id'] = menu.action.id
            redirect_url = redirect_url%params
            leave_link = urljoin(base_url, redirect_url)
        
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            for first_level_app in employee.first_level_app_id:
                if first_level_app.id not in approvers:
                    approvers.append(first_level_app.id)
            for second_level_app in employee.second_level_app_id:
                if second_level_app.id not in approvers:
                    approvers.append(second_level_app.id)
            for third_level_app in employee.third_level_app_id:
                if third_level_app.id not in approvers:
                    approvers.append(third_level_app.id)
                          
        if approvers:
            for approver in approvers:
                leave_by_employee = self.env['hr.holidays'].search([('type','=','remove'),('state','in',['confirm','1','2']),'|',('employee_id.first_level_app_id','in',[approver]),'|',('employee_id.second_level_app_id','in',[approver]),('employee_id.third_level_app_id','in',[approver])])
                if leave_by_employee:
                    applicants = []
                    for leave in leave_by_employee:
                        if leave.employee_id.name not in applicants:
                            applicants.append(leave.employee_id.name)
                    template_id = self.env.ref('ltpl_hr_holidays_modification.leave_request_email_notification')
                    email_to = self.env['hr.employee'].search([('user_id','=',approver)]).work_email
                    total_unapproved_leave = len(leave_by_employee)                   
                    template_id.with_context(email_to = email_to,total_unapproved_leave=total_unapproved_leave,applicants=applicants,leave_link=leave_link).send_mail(approver, force_send=True)
                    
    @api.multi               
    def leave_request_cancel_reminder_notification(self):
        approvers = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        params = {}
        redirect_url = '/web#view_type=list&model=hr.holidays&menu_id=%(menu_id)d&action=%(action_id)d'
        ir_model_obj = self.env['ir.model.data']
        menu_model,menu_id = ir_model_obj.sudo().get_object_reference('hr_holidays', 'menu_hr_holidays_root')
        submenu_model,sub_menu_id = ir_model_obj.sudo().get_object_reference('ltpl_hr_holidays_modification', 'menu_open_department_leave_cancel_approve')
        leave_link = ""
        if menu_id:
            params['menu_id'] = menu_id
            menu = self.env['ir.ui.menu'].sudo().search([("id","=",sub_menu_id)])
            params['action_id'] = menu.action.id
            redirect_url = redirect_url%params
            leave_link = urljoin(base_url, redirect_url)
        
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            for first_level_app in employee.first_level_app_id:
                if first_level_app.id not in approvers:
                    approvers.append(first_level_app.id)
            for second_level_app in employee.second_level_app_id:
                if second_level_app.id not in approvers:
                    approvers.append(second_level_app.id)
            for third_level_app in employee.third_level_app_id:
                if third_level_app.id not in approvers:
                    approvers.append(third_level_app.id)
        print(approvers)        
        if approvers:
            for approver in approvers:
                leave_by_employee = self.env['hr.holidays'].search([('type','=','remove'),('state','in',['apply_cancel','cancel_1','cancel_2','cancel_3']),'|',('employee_id.first_level_app_id','in',[approver]),'|',('employee_id.second_level_app_id','in',[approver]),('employee_id.third_level_app_id','in',[approver])])
                if leave_by_employee:
                    applicants = []
                    for leave in leave_by_employee:
                        if leave.employee_id.name not in applicants:
                            applicants.append(leave.employee_id.name)
                    template_id = self.env.ref('ltpl_hr_holidays_modification.leave_cancel_request_email_notification')
                    email_to = self.env['hr.employee'].search([('user_id','=',approver)]).work_email
                    total_unapproved_leave = len(leave_by_employee)                   
                    template_id.with_context(email_to = email_to,total_unapproved_leave=total_unapproved_leave,applicants=applicants,leave_link=leave_link).send_mail(approver, force_send=True)