import json
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, ModelFormMixin, UpdateView, DeleteView
from django.views.generic.list import ListView
from cratis.app.core.common.i18n import find_by_localized_field
from cratis.app.ecommerce.orders.models import Address, Order
from cratis.app.ecommerce.profile.models import UserProfile
from cratis.app.ecommerce.products.models import ProductCategory

__author__ = 'Alex'


class WithShopingCartMixin(object):

    def get_context_data(self, **kwargs):
        context = super(WithShopingCartMixin, self).get_context_data(**kwargs)


        return context

class WithSidebarMixin(object):

    def get_context_data(self, **kwargs):
        context = super(WithSidebarMixin, self).get_context_data(**kwargs)

        if 'category_slug' in self.kwargs:
            loc_cat = find_by_localized_field(ProductCategory, 'slug', self.kwargs['category_slug'])
            if loc_cat:
                self.kwargs['category_id'] = loc_cat.id

        if 'category_id' in self.kwargs:
            context['cur_category'] = ProductCategory.objects.get(pk=self.kwargs['category_id'])

        return context

class Profile(WithShopingCartMixin, TemplateView):
    template_name= 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)

        # address list
        profile = self.request.user.get_profile()

        context['profile'] = profile

        context['address_list'] = Address.objects.filter(profile=profile)


        context['orders_confirmed'] = Order.objects.filter(user=profile, status=Order.ORDER_STATUS_CONFIRMED)
        context['orders_paid'] = Order.objects.filter(user=profile, status=Order.ORDER_STATUS_PAID)
        context['orders_completed'] = Order.objects.filter(user=profile, status=Order.ORDER_STATUS_COMPLETED)
        context['orders_rejected'] = Order.objects.filter(user=profile, status=Order.ORDER_STATUS_REJECTED)

        return context


class ProfileAddressList(WithShopingCartMixin, ListView):

    template_name= 'profile/address_list.html'
    model = Address

    def get_queryset(self):
        q = super(ProfileAddressList, self).get_queryset()

        profile = self.request.user.get_profile()
        return q.filter(profile=profile)

class ProfileOrderList(WithShopingCartMixin, ListView):

    template_name= 'profile/order_list.html'
    model = Order

    def get_queryset(self):
        q = super(ProfileOrderList, self).get_queryset()

        profile = self.request.user.get_profile()
        return q.filter(user=profile)

class ProfileOrderDetails(WithShopingCartMixin, DetailView):

    template_name= 'profile/order_details.html'
    model = Order
    context_object_name = 'order'

    def get_queryset(self):
        q = super(ProfileOrderDetails, self).get_queryset()

        profile = self.request.user.get_profile()
        return q.filter(user=profile)
#
class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ('profile', 'temporary', 'is_main', 'recipient', 'country')

class ProfileAddressNew(WithShopingCartMixin, CreateView):
    template_name= 'profile/address_new.html'
    model = Address
    form_class = AddressForm

    def get_success_url(self):
        return reverse('profile')




    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.get_profile()
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

@require_POST
def update_address(request, id):

    address = Address.objects.get(pk=int(id))

    if not address or address.profile.pk != request.user.get_profile().pk:
        return HttpResponse(json.dumps({'ok':False, 'message': 'Not authorized'}), mimetype='application/javascript')


    if 'country' in request.POST:
        address.country = request.POST['country']
    address.city = request.POST['city']
    address.street_address = request.POST['street_address']
    address.lastname = request.POST['lastname']
    address.firstname = request.POST['firstname']
    address.post_index = request.POST['post_index']
    address.phone = request.POST['phone']
    address.email = request.POST['email']
    address.save()

    return HttpResponse(json.dumps({'ok':True}), mimetype='application/javascript')



def make_address_default(request, id):
    profile = request.user.get_profile()
    for address in profile.saved_adresses():
        address.is_main = (address.pk == int(id))
        address.save()

    return HttpResponseRedirect(reverse('profile'))



class ProfileAddressEdit(WithShopingCartMixin, UpdateView):
    template_name= 'profile/address_edit.html'
    model = Address
    form_class = AddressForm

    def get_queryset(self):
        q = super(ProfileAddressEdit, self).get_queryset()
        profile = self.request.user.get_profile()
        return q.filter(profile=profile)


    def get_success_url(self):
        return reverse('profile')

class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

class ProfileEdit(WithShopingCartMixin, UpdateView):
    template_name= 'profile/edit.html'
    model = UserProfile
    form_class = ProfileForm

    def get_object(self, queryset=None):
        profile = self.request.user.get_profile()
        return profile

    def get_success_url(self):
        return reverse('profile')

class ProfileAddressRemove(WithShopingCartMixin, DeleteView):
    model = Address

    template_name = 'profile/address_confirm_delete.html'

    def get_queryset(self):
        q = super(ProfileAddressRemove, self).get_queryset()
        profile = self.request.user.get_profile()
        return q.filter(profile=profile)

    def get_success_url(self):
        return reverse('profile')








