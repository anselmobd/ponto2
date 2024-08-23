from pprint import pprint


__all__ = [
    'form_report',
]


def form_report(form, form_report_excludes=[]):
    if hasattr(form, 'field_control'):
        field_control = form.field_control
    else:
        field_control = [[key] for key in form.fields.keys()]

    result = []
    for lin in field_control:
        line = {}
        for col in lin:
            if col in form_report_excludes:
                continue
            value = form.cleaned_data[col]
            if form.fields[col].widget.input_type == 'select':
                value = dict(form.fields[col].choices)[value]
            if value:
                if not (label := form.fields[col].label):
                    label = col.title()
                line[label] = value
        if line:
            result.append(line)

    return result
