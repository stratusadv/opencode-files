---
name: permissions
description: Django Spire permission patterns, cascading structure, and conventions
---

# Django Spire Permissions

## Overview

Django Spire uses standard Django permission decorators on function-based views (FBVs) with a cascading permission structure where child apps inherit parent app permissions. Understanding app labels and the cascading system is critical for correct permission implementation.

## Core Concepts

### App Labels

Permissions are formatted as `{app_label}.{action}_{model_name}`. The app label comes from the `label` field in `AppConfig`, not the directory name. Always verify the actual app label in `apps.py` or `admin.py` before writing permissions.

```python
# app/inventory/apps.py
class InventoryConfig(AppConfig):
    label = 'inventory'  # Permission prefix = 'inventory.*'
    name = 'app.inventory'
```

### Cascading Permission Structure

Child apps inherit parent app permissions through `MODEL_PERMISSIONS` in their app config. This means sub-apps do not need their own permissions—a user with `inventory.change_inventory` can manage inventory records, events, and batches without explicit `inventory_record.change_inventory_record` permissions.

```python
# app/inventory/record/apps.py
class InventoryRecordConfig(AppConfig):
    label = 'inventory_record'
    name = 'app.inventory.record'
    MODEL_PERMISSIONS = (
        {
            'name': 'inventory_record',
            'model_class_path': 'app.inventory.models.Inventory',
            'is_proxy_model': False,
        },
    )
```

With this configuration, `inventory.record` views check `inventory.*` permissions instead of `inventory_record.*` permissions.

### Standard Permission Actions

| Action | Usage |
|--------|-------|
| `add_{model}` | Create operations |
| `change_{model}` | Update operations and edit buttons |
| `delete_{model}` | Delete operations |
| `view_{model}` | Read operations and list/detail views |

### Special Permissions

Special permissions follow the `can_{action}` pattern and represent non-standard operations like workflow actions, locking, or status advancement. Define them in the model's `Meta.permissions` tuple.

```python
# app/sales/purchase_order/models.py
class SalesPurchaseOrder(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Sales Purchase Order'
        permissions = [
            ('can_lock_sales_orders', 'Can Lock Sales Orders'),
            ('can_advance_sales_order_status', 'Can Advance Sales Order Status'),
        ]
```

In views, use `request.user.has_perm()` for programmatic checks:

```python
if not request.user.has_perm('sales_purchase_order.can_advance_sales_order_status'):
    return JsonResponse({'type': 'error', 'message': 'Permission denied'})
```

In templates, use `{% if perms.app.can_action %}`:

```django
{% if perms.sales_purchase_order.can_lock_sales_orders %}
    <button hx-post="{% url 'sales:purchase_order:json:lock' pk=order.pk %}">
        {% if order.is_locked %}Unlock{% else %}Lock{% endif %}
    </button>
{% endif %}
```

## Implementation Guide

### Views

Apply `@permission_required` to FBVs. Use the parent app's permission for sub-apps.

```python
# Standard app
@permission_required('inventory.add_inventory')
def create_view(request):
    ...

# Sub-app using parent permissions
@permission_required('inventory.change_inventory')
def update_view(request, pk):
    ...
```

### Templates

Use `{% if perms.app_label.action_model %}` to conditionally render UI elements.

### Custom Permissions

Define in `Model.Meta.permissions` and use with `request.user.has_perm()` or `{% if perms.app.can_custom_permission %}`.

## Examples

### Inventory Record Module

The `inventory.record` module demonstrates cascading permissions. All CRUD operations check `inventory.*` permissions despite the app label being `inventory_record`.

```python
# app/inventory/record/views/form_views.py
@permission_required('inventory.add_inventory')
def create_view(request: WSGIRequest) -> TemplateResponse:
    form = self.form_class(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(self.success_url)
    return render(request, self.template_name, {'form': form})

@permission_required('inventory.change_inventory')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    record = get_object_or_404(models.InventoryRecord, pk=pk)
    form = self.form_class(request.POST or None, instance=record)
    if form.is_valid():
        form.save()
        return redirect(self.success_url)
    return render(request, self.template_name, {'form': form})

@permission_required('inventory.delete_inventory')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    record = get_object_or_404(models.InventoryRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        return redirect(self.success_url)
    return render(request, self.template_name, {'record': record})
```

```django
<!-- templates/inventory/record/list_page.html -->
{% if perms.inventory.add_inventory %}
    <a href="{% url 'inventory:record:form:create' %}" class="btn btn-primary">
        Add Record
    </a>
{% endif %}

{% if perms.inventory.view_inventory %}
    <ul>
    {% for record in records %}
        <li>
            {{ record.name }}
            {% if perms.inventory.change_inventory %}
                <a href="{% url 'inventory:record:form:update' pk=record.pk %}">Edit</a>
            {% endif %}
        </li>
    {% endfor %}
    </ul>
{% endif %}
```

### App Structure Example

```python
# app/company/apps.py
class CompanyConfig(AppConfig):
    label = 'company'
    name = 'app.company'
    MODEL_PERMISSIONS = (
        {'name': 'company', 'model_class_path': 'app.company.models.Company', ...},
    )

# app/company/location/apps.py
class CompanyLocationConfig(AppConfig):
    label = 'company_location'
    name = 'app.company.location'
    MODEL_PERMISSIONS = (
        {'name': 'location', 'model_class_path': 'app.company.models.Company', ...},
    )
```

Both `company` and `company.location` apps use `company.*` permissions. A user needs `company.view_company` to view both companies and company locations.

## Do's and Don'ts

Do not create separate permissions for every nested app. Leverage cascading—grant parent app permissions to access all sub-app functionality.

Do not assume the app label matches the directory name. Always verify in `apps.py` or `admin.py`.

Do not skip permission checks in templates when views are decorated. Template-level checks provide UI filtering that decorator-level checks cannot.

## Code Review Checklist

When reviewing permission code, verify the following:

1. **App Label**: Confirm the app label matches `AppConfig.label`, not the directory or module name
2. **Cascading Consistency**: For nested apps, verify they reference parent app permissions via `MODEL_PERMISSIONS`
3. **View Decorators**: Ensure all FBVs have appropriate `@permission_required` decorators
4. **Template Checks**: Verify template permission checks match view decorators
5. **Action Mapping**: Check that CRUD operations use the correct action (`add`, `change`, `delete`, `view`)
6. **Special Permissions**: Verify `can_*` permissions are defined in `Meta.permissions` with descriptive names
7. **Custom Permissions**: For custom permissions, verify both definition in `Meta.permissions` and usage in views/templates
8. **Conditional Links**: For links that change between clickable and plain text, verify both branches are handled
8. **OR Conditions**: When using `or` for multiple permission checks, confirm at least one valid app label is used
9. **Workflow Permissions**: For workflow buttons, verify custom permissions are defined in the model's `Meta.permissions`
10. **No Direct Permission Creation**: Permissions should not be manually created in migrations or scripts—rely on Django's permission system