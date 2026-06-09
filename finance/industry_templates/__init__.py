"""
行业模板模块 - 在会计制度基础上定制行业特有科目
"""
from industry_templates.registry import get_template, get_available_templates, customize_accounts, register

# 注册所有内置行业模板
from industry_templates.real_estate import RealEstateTemplate
from industry_templates.commercial import CommercialTemplate
from industry_templates.manufacturing import ManufacturingTemplate
from industry_templates.construction import ConstructionTemplate
from industry_templates.catering import CateringTemplate

register('real_estate', RealEstateTemplate)
register('commercial', CommercialTemplate)
register('manufacturing', ManufacturingTemplate)
register('construction', ConstructionTemplate)
register('catering', CateringTemplate)