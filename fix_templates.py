#!/usr/bin/env python3
"""
Script to convert Flask template syntax to Django template syntax
"""
import os
import re

# Mapping of Flask route names to Django URL names
URL_MAPPINGS = {
    "url_for('main.dashboard')": "{% url 'dashboard' %}",
    "url_for('auth.login')": "{% url 'login' %}",
    "url_for('auth.register')": "{% url 'register' %}",
    "url_for('auth.logout')": "{% url 'logout' %}",
    "url_for('orders.list_orders')": "{% url 'order-list' %}",
    "url_for('orders.create_order')": "{% url 'order-create' %}",
    "url_for('vehicles.list_vehicles')": "{% url 'vehicle-list' %}",
    "url_for('vehicles.create_vehicle')": "{% url 'vehicle-create' %}",
    "url_for('main.tracking')": "{% url 'telemetry' %}",
    "url_for('main.delivery_prediction')": "{% url 'prediction' %}",
    "url_for('main.bin_packing')": "{% url 'bin-packing' %}",
}

def fix_template(filepath):
    """Fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Replace {{ url_for(...) }} with {% url ... %}
        for flask_syntax, django_syntax in URL_MAPPINGS.items():
            pattern = r'\{\{\s*' + re.escape(flask_syntax) + r'\s*\}\}'
            if re.search(pattern, content):
                content = re.sub(pattern, django_syntax, content)
                changes_made = True
        
        # Replace {{ form.hidden_tag() }} with {% csrf_token %}
        if '{{ form.hidden_tag() }}' in content:
            content = content.replace('{{ form.hidden_tag() }}', '{% csrf_token %}')
            changes_made = True
        
        # Save if changes were made
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⏭️  Skipped: {filepath} (no changes needed)")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all templates"""
    templates_dir = r'c:\Users\Abubakkar Raza\Downloads\projects\SK\templates'
    
    fixed_count = 0
    total_count = 0
    
    # Walk through all HTML files
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                total_count += 1
                if fix_template(filepath):
                    fixed_count += 1
    
    print(f"\n{'='*60}")
    print(f"✨ Template Fix Complete!")
    print(f"{'='*60}")
    print(f"Total templates scanned: {total_count}")
    print(f"Templates fixed: {fixed_count}")
    print(f"Templates unchanged: {total_count - fixed_count}")

if __name__ == '__main__':
    main()
