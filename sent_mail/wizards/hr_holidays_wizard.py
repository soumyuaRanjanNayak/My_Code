# -*- coding: utf-8 -*-
# Part of LTPL. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class ltpl_hr_holidays_wizard(models.TransientModel):
    _name = "hr.holidays.wizard"
    _description = "Approve Multiple Holidays"  
            
    def approve_multiple_holidays(self):
        context = self.env.context
        hr_holidays_obj = self.env['hr.holidays']
        active_holiday_ids = context['active_ids']

        for leave_data in hr_holidays_obj.search([('id','in',active_holiday_ids),('state','not in',['apply_cancel','cancel_1','cancel_2','cancel_3','cancel'])]):
            leave_data.action_approve()
            
        for leave_data in hr_holidays_obj.search([('id','in',active_holiday_ids),('state','in',['apply_cancel','cancel_1','cancel_2','cancel_3','cancel'])]):
            leave_data.action_cancel()
        
        return self.return_view('ltpl_approve_holidays_form_done') 
    
    def return_view(self, name):
        ir_model_obj = self.env['ir.model.data']
        result = ir_model_obj.get_object_reference('ltpl_hr_holidays_modification', name)
        view_id = result and result[1] or False
        r = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.holidays.wizard',
            'views': [(view_id, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
        return r
    
    
    


