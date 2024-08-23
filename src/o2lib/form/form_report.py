from pprint import pprint


__all__ = [
    'form_report',
]


def form_report(form, form_report_excludes=[], field_modifier={}):
    if hasattr(form, 'field_control'):
        field_control = form.field_control
    else:
        field_control = [[key] for key in form.fields.keys()]

    result = []
    for lin in field_control:
        line = {}
        for field in lin:
            if field in form_report_excludes:
                continue
            value = form.cleaned_data[field]
            if form.fields[field].widget.input_type == 'select':
                value = dict(form.fields[field].choices)[value]
            if field in field_modifier:
                value = field_modifier[field](value)
            if value:
                if not (label := form.fields[field].label):
                    label = field.title()
                line[label] = value
        if line:
            result.append(line)

    return result
