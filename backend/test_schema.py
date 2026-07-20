import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'app'))
from schemas.comparison import PricingComparison

data = {
    'pricing_breakdown': {
        'Agency A': '$17,000.00',
        'Agency B': '15,000',
        'Agency C': 'USD 20000',
        'Agency D': '18,000 AED',
        'Agency E': 12000
    }
}
try:
    obj = PricingComparison(**data)
    print(obj.pricing_breakdown)
except Exception as e:
    print('Failed:', e)
