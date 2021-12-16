from json.encoder import JSONEncoder
import json

from django.core.checks import messages
from django.db import models
from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.http import request
from django.shortcuts import redirect, render
from django.utils.translation import templatize
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from inventory import models as inv_models
from inventory import forms as inv_forms
from authentications import models as auth_models
from django.urls import reverse_lazy
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Create your views here.

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ home page ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Home(LoginRequiredMixin, TemplateView ):
    template_name = "inventory/Home.html"


#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ test classes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Test(LoginRequiredMixin, TemplateView):
    template_name = "pages/table.html"
    model = inv_models.Propertys
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"form":inv_forms.Test_form})
        return context

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ add and list items ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Add_items(LoginRequiredMixin, CreateView):
    model = inv_models.Items
    form_class = inv_forms.Add_items_form
    template_name = "inventory/item/add_item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"categories":inv_models.Category.objects.all()})
        return context

    def get_success_url(self):
        return reverse_lazy('Add_placement_value', args=(self.object.id,))


class Add_placement_value(LoginRequiredMixin, TemplateView):
    model = inv_models.Items
    form_class = inv_forms.Add_items_form
    template_name = "inventory/item/add_item_placement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "stores":inv_models.Store.objects.all(),
            "shelfs":inv_models.Shelf.objects.all(),
        })
        return context
    
    
    def post(self, request, *args, **kwargs):
        print(request.POST)
        item = inv_models.Items.objects.get(id=kwargs['pk'])
        item.store = inv_models.Store.objects.get( id = request.POST.get('store'))
        item.shelf = inv_models.Shelf.objects.get(id = request.POST.get('shelf'))
        item.save()
        return redirect(reverse_lazy('Add_measurement_value', args=(kwargs['pk'],)))


class Add_measurement_value(LoginRequiredMixin, ListView):
    model = inv_models.Items
    template_name = "inventory/item/add_item_mesurement.html"
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "measurements":inv_models.Measurement.objects.all(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        # print(request.POST)
        for measurement in request.POST:
            if request.POST.get('csrfmiddlewaretoken') != request.POST.get(measurement) and '' != request.POST.get(measurement):
                measurement_value = measurement.split('-')
                property = inv_models.Propertys(item=inv_models.Items.objects.get(id=int(kwargs['pk'])), measurement=inv_models.Measurement.objects.get(id=int(measurement_value[1])), value=request.POST.get(measurement))
                property.save()
            
        return redirect(reverse_lazy("List_items"))
    
class List_items(LoginRequiredMixin, ListView):
    template_name = "inventory/item/list_item.html"
    model = inv_models.Items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "measurements":inv_models.Measurement.objects.all(),
            "properties":inv_models.Propertys.objects.all(),
        })
        return context
    
class Update_item(LoginRequiredMixin, UpdateView):
    template_name = "inventory/item/update_item.html"
    model = inv_models.Items
    form_class = inv_forms.Update_item_form
    success_url = reverse_lazy("List_items")

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context.update({"categories":inv_models.Category.objects.all()})
        return context

class Detail_item(LoginRequiredMixin, DetailView):
    template_name = "inventory/item/detial_item.html"
    model = inv_models.Items
    success_url = reverse_lazy("List_items")

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ add and list measurement ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Add_measurements(LoginRequiredMixin, CreateView):
    model = inv_models.Measurement
    form_class = inv_forms.Add_mesurement_form
    template_name = "inventory/measurement/add_measurement.html"
    success_url = reverse_lazy("List_measurements")

class List_measurements(LoginRequiredMixin, ListView):
    model = inv_models.Measurement
    template_name = "inventory/measurement/list_measurement.html"


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ add and list category ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Add_categories(LoginRequiredMixin, CreateView):
    model = inv_models.Category
    form_class = inv_forms.Add_category_form
    template_name = "inventory/category/add_category.html"
    success_url = reverse_lazy("List_categories")

    
class List_categories(LoginRequiredMixin, ListView):
    model = inv_models.Category
    template_name = "inventory/category/list_category.html"

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ add and list store ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Add_store(LoginRequiredMixin, CreateView):
    model = inv_models.Store
    form_class = inv_forms.Add_store_form
    template_name = "inventory/store/add_store.html"

    def form_valid(self, form):
        store = inv_models.Store(name = form.cleaned_data["name"], location = form.cleaned_data["location"], 
            user = self.request.user,max_capacity=form.cleaned_data["max_capacity"])
        store.save()

        return redirect (reverse_lazy("List_store"))


class List_store(LoginRequiredMixin, ListView):
    model = inv_models.Store
    template_name = "inventory/store/list_store.html"

class Detail_store(LoginRequiredMixin, DetailView):
    model = inv_models.Store
    template_name = "inventory/store/detail_store.html"
    success_url = reverse_lazy("List_store")

class Update_store(LoginRequiredMixin, UpdateView):
    model = inv_models.Store
    template_name = "inventory/store/update_store.html"
    form_class = inv_forms.Update_store_form
    success_url = reverse_lazy("List_store")

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ add and list shelf ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
class Add_shelf(LoginRequiredMixin, CreateView):
    model = inv_models.Shelf
    form_class = inv_forms.Add_shelf_form
    template_name = "inventory/shelf/add_shelf.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'stores': inv_models.Store.objects.all()})
        return context
    
    def form_valid(self, form):
        shelfs_count = len(inv_models.Shelf.objects.filter(store=form.cleaned_data["store"]))
        if(shelfs_count < form.cleaned_data["store"].max_capacity): 
            shelf = inv_models.Shelf(name=form.cleaned_data["name"],store=form.cleaned_data["store"],
                description=form.cleaned_data["description"],max_capacity=form.cleaned_data["max_capacity"])
            shelf.save()

            return redirect(reverse_lazy("List_shelf"))
        else:
            return redirect(reverse_lazy("Capacity_error"))
        
        
class List_shelf(LoginRequiredMixin, ListView):
    model = inv_models.Shelf
    template_name = "inventory/shelf/list_shelf.html"

class Detail_shelf(LoginRequiredMixin, DetailView):
    model = inv_models.Shelf
    template_name = "inventory/shelf/detail_shelf.html"

class Update_shelf(LoginRequiredMixin, UpdateView):
    model = inv_models.Shelf
    template_name = "inventory/shelf/update_shelf.html"
    form_class = inv_forms.Update_shelf_form
    success_url = reverse_lazy("List_shelf")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"stores":inv_models.Store.objects.all()})
        return context

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ Add and List request ++++++++++++++++++++++++++++++++++++++++++++
class Add_request(LoginRequiredMixin, TemplateView):
    template_name = "inventory/request/add_request.html"
    # model = inv_models.Request
    success_url = reverse_lazy("List_request")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "formset":inv_forms.Add_requestrow_formset(),
            "user":self.request.user,
            "items":inv_models.Items.objects.all(),
            "request_notifications":inv_models.Request.objects.filter(status="Pending"),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode("utf-8"))
        request_model = inv_models.Request(request_by = self.request.user)
        request_model.remark = post_data["remark"]
        request_model.save()
        items = {}

        for data in post_data["data"]:
            item = inv_models.Items.objects.get(id=post_data["data"][data]["item_label"])
            if item in items:
                items[item]+= int(post_data["data"][data]['quantity_label'])
            else:
                items[item] = int(post_data["data"][data]['quantity_label'])
        for row in items:
            requestrow_model= inv_models.RequestRow(item=row, request = request_model, requested_amount=items[row])    
            requestrow_model.save()
        return redirect(reverse_lazy("List_request"))
        

class List_request(LoginRequiredMixin, ListView):
    template_name = "inventory/request/list_request.html"
    model = inv_models.Request
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "request_notifications":len(inv_models.Request.objects.filter(status="Pending")),
        })
        return context

class Detail_request(LoginRequiredMixin, DetailView):
    model = inv_models.Request
    template_name = "inventory/request/detail_request.html"

class Update_request(LoginRequiredMixin, TemplateView):
    model = inv_models.Request
    template_name = "inventory/request/update_request.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "request":inv_models.Request.objects.get(id=kwargs["pk"]),
            "users":auth_models.User.objects.all(), 
        })
        return context
    
    def post(self, request, *args, **kwargs):
        request_list = inv_models.Request.objects.get(id=kwargs["pk"])
        for response in request.POST:
            if response == "csrfmiddlewaretoken":
                pass
            elif response == "name-field":
                request_list.user = auth_models.User.objects.get(id=request.POST.get(response))
            else:
                res = response.split("-")
                print(request.POST.get(response))
                request_row = inv_models.RequestRow.objects.get(id=res[0])
                request_row.requested_amount = request.POST.get(response)
                request_row.save()
        request_list.save()
        return redirect(reverse_lazy("List_request"))
                

            
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ Errors ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Capacity_error(LoginRequiredMixin, TemplateView):
    template_name = "inventory/capacity_error.html"