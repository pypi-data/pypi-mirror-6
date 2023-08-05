from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from cratis.app.i18n.utils import localize_url as _
from cratis.app.ecommerce.profile.views import Profile, ProfileAddressList, ProfileAddressNew, ProfileOrderList, ProfileOrderDetails, ProfileAddressEdit, ProfileAddressRemove, ProfileEdit
from cratis.app.ecommerce.products.sitemap import ProductCategorySitemap, ProductSitemap
from cratis.app.ecommerce.products.views import MainPageListView, ProductView, SearchListView, all_products_xml

sitemaps = {
    'categories': ProductCategorySitemap(),
    'products': ProductSitemap(),
    }

urlpatterns = patterns('',

    url(_(r'^$'), MainPageListView.as_view(), name='main_page'),

    url(r'^sitemap\.xml$', 'cratis.app.ecommerce.products.sitemap.sitemap', {'sitemaps': sitemaps}),
    url(r'^afesf322fs32fefwkj32iiwefw/all_products\.xml$', all_products_xml),

    url(_(r'^product/all/$'), SearchListView.as_view(), name='all_products'),
    url(_(r'^product/$'), SearchListView.as_view()),

    url(_(r'^product/(?P<category_id>\d+)$'),
        SearchListView.as_view(),
        name='products_in_category'
    ),

    url(_(r'^product/all/(?P<pk>\d+)$'),
        ProductView.as_view(),
        name='product'
    ),

    url(_(r'^product/(?P<category_id>\d+)/(?P<pk>\d+)$'),
        ProductView.as_view(),
        name='product_with_cat'
    ),

    url(_(r'^product/all/(?P<slug>[^/]+)$'),
        ProductView.as_view(),
        name='product_by_slug'
    ),

    url(_(r'^product/(?P<category_slug>[^/]+)$'),
        SearchListView.as_view(),
        name='products_in_category_by_slug'
    ),

    url(_(r'^product/(?P<category_slug>[^/]+)/(?P<pk>\d+)$'),
        ProductView.as_view(),
        name='product_with_cat_cat_by_slug_prod_by_id'
    ),

    url(_(r'^product/(?P<category_id>\d+)/(?P<slug>[^/]+)$'),
        ProductView.as_view(),
        name='product_with_cat_cat_by_id_prod_by_slug'
    ),

    url(_(r'^product/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)$'),
        ProductView.as_view(),
        name='product_with_cat_both_by_slug'
    ),


    url(_(r'^profile/$'),
        Profile.as_view(),
        name='profile'
    ),

    url(_(r'^profile/edit$'),
        ProfileEdit.as_view(),
        name='profile_edit'
    ),

    url(_(r'^profile/address/$'),
        ProfileAddressList.as_view(),
        name='profile_address'
    ),
    url(_(r'^profile/address/make_default/(?P<id>\d+)$'),
        'cratis.app.ecommerce.profile.views.make_address_default',
        name='profile_address_make_default'
    ),
    url(_(r'^profile/address/update_address/(?P<id>\d+)$'),
        'cratis.app.ecommerce.profile.views.update_address',
        name='profile_update_address'
    ),
    url(_(r'^profile/orders/$'),
        ProfileOrderList.as_view(),
        name='profile_orders'
    ),
    url(_(r'^profile/orders/detail/(?P<pk>\d+)$'),
        ProfileOrderDetails.as_view(),
        name='profile_order_details'
    ),

    url(_(r'^profile/address/new$'),
        ProfileAddressNew.as_view(),
        name='profile_address_new'
    ),

    url(_(r'^profile/address/edit/(?P<pk>\d+)$'),
        ProfileAddressEdit.as_view(),
        name='profile_address_edit'
    ),


    url(_(r'^profile/address/remove/(?P<pk>\d+)$'),
        ProfileAddressRemove.as_view(),
        name='profile_address_remove'
    ),

    url(r'^compare/add/(?P<product_id>\d+)$', 'cratis.app.ecommerce.products.views.add_to_compare', name='compare_add'),
    url(r'^compare/clear$', 'cratis.app.ecommerce.products.views.clear_compare', name='compare_clear'),
    url(r'^compare/render$', 'cratis.app.ecommerce.products.views.render_compare', name='compare_render'),

    url(r'^order/reject/(?P<order_id>\d+)$', 'cratis.app.ecommerce.products.views.reject_order', name='reject_order'),
    url(r'^order/repeat/(?P<order_id>\d+)$', 'cratis.app.ecommerce.products.views.repeat_order', name='repeat_order'),

    url(r'^trans$', 'cratis.app.ecommerce.products.views.trans'),
    url(r'^type-ac/(?P<type>\d+)$', 'cratis.app.ecommerce.products.views.attr_type'),

    url(_(r'^ajax-auth/login$'), 'cratis.app.ecommerce.products.views.ajax_login', name='ajax_login'),
    url(_(r'^ajax-auth/register$'), 'cratis.app.ecommerce.products.views.ajax_register', name='ajax_register'),
    url(_(r'^ajax-auth/password_restore$'), 'cratis.app.ecommerce.products.views.ajax_password_restore', name='ajax_password_restore'),

)
