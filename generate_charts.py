import json
import math
import os
import re

def get_proficiency(exp):
    if exp >= 48:
        return 'Expert'
    elif exp >= 18:
        return 'Advanced'
    elif exp >= 8:
        return 'Intermediate'
    else:
        return 'Beginner'

def create_donut_svg(data, title, colors, filename):
    total = sum(d['value'] for d in data)
    if total == 0:
        return
    
    width = 280
    legend_cols = 2
    legend_rows = math.ceil(len(data) / legend_cols)
    legend_row_height = 20
    
    center_x = width / 2
    # Shifted the center of the chart down to 125 so the title doesn't overlap
    center_y = 125
    radius = 70
    inner_radius = 40
    
    legend_y_start = center_y + radius + 25
    height = legend_y_start + (legend_rows * legend_row_height) + 10
    
    svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '''<style>
    .title { fill: #24292e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 14px; font-weight: bold; }
    .legend { fill: #57606a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; }
    .legend.expert { font-weight: bold; fill: #b8860b; }
    .legend.advanced { font-weight: 600; fill: #24292e; }
    .legend.intermediate { font-weight: normal; }
    .legend.beginner { font-style: italic; opacity: 0.8; }
    @media (prefers-color-scheme: dark) {
      .title { fill: #c9d1d9; }
      .legend { fill: #8b949e; }
      .legend.expert { fill: #e3b341; }
      .legend.advanced { fill: #c9d1d9; }
    }
    .arc { transition: opacity 0.2s; stroke: #ffffff; stroke-width: 1.5px; }
    @media (prefers-color-scheme: dark) {
      .arc { stroke: #0d1117; }
    }
    .arc:hover { opacity: 0.8; }
  </style>\n'''
    
    # Title placed at the top (y=25) instead of the middle of the chart to prevent overlap
    import html
    safe_title = html.escape(title)
    svg += f'<text class="title" x="{center_x}" y="25" dominant-baseline="middle" text-anchor="middle">{safe_title}</text>\n'
    
    current_angle = -math.pi / 2
    
    for i, item in enumerate(data):
        value = item['value']
        if value == 0:
            continue
            
        angle = (value / total) * 2 * math.pi
        next_angle = current_angle + angle
        
        if angle >= 2 * math.pi - 0.001:
            angle = 2 * math.pi - 0.001
            
        x1 = center_x + radius * math.cos(current_angle)
        y1 = center_y + radius * math.sin(current_angle)
        x2 = center_x + radius * math.cos(next_angle)
        y2 = center_y + radius * math.sin(next_angle)
        
        x3 = center_x + inner_radius * math.cos(next_angle)
        y3 = center_y + inner_radius * math.sin(next_angle)
        x4 = center_x + inner_radius * math.cos(current_angle)
        y4 = center_y + inner_radius * math.sin(current_angle)
        
        large_arc_flag = 1 if angle > math.pi else 0
        color = colors[i % len(colors)]
        
        path = f'<path class="arc" d="M {x1} {y1} A {radius} {radius} 0 {large_arc_flag} 1 {x2} {y2} L {x3} {y3} A {inner_radius} {inner_radius} 0 {large_arc_flag} 0 {x4} {y4} Z" fill="{color}" />'
        
        title_text = f'{item["label"]} - {item.get("proficiency", "Unknown")}'
        path = f'<g><title>{title_text}</title>{path}</g>\n'
        svg += path
        current_angle = next_angle
        
    for i, item in enumerate(data):
        col = i % legend_cols
        row = i // legend_cols
        lx = col * (width / legend_cols) + 10
        ly = legend_y_start + row * legend_row_height
        
        color = colors[i % len(colors)]
        svg += f'<rect x="{lx}" y="{ly - 8}" width="8" height="8" fill="{color}" rx="2" />\n'
        
        label = item["label"]
        if len(label) > 23:
            label = label[:20] + "..."
        prof_class = item.get("proficiency", "").lower()
        svg += f'<text class="legend {prof_class}" x="{lx + 14}" y="{ly}">{label}</text>\n'
        
    svg += '</svg>'
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9]+', '_', name).strip('_').lower()

def main():
    with open('metrics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    palette = ['#00599C', '#ED8B00', '#3670A0', '#239120', '#F7DF1E', '#5C2D91', '#E34F26', '#41B883', '#009688', '#D24939', '#0db7ed', '#2671E5', '#6DB33F', '#000000', '#333333']
    
    categories = data.get('categories', [])
    
    for cat in categories:
        cat_name = cat.get('name')
        items = cat.get('stack', [])
        
        chart_data = []
        for item in items:
            name = item.get('name')
            exp = item.get('length_of_exp', 0)
            prof = get_proficiency(exp)
            if exp > 0:
                chart_data.append({'label': f"{name} ({exp})", 'value': exp, 'proficiency': prof})
        
        if chart_data:
            chart_data.sort(key=lambda x: x['value'], reverse=True)
            filename = f"svgs/{sanitize_filename(cat_name)}.svg"
            create_donut_svg(chart_data, cat_name, palette, filename)

if __name__ == '__main__':
    main()