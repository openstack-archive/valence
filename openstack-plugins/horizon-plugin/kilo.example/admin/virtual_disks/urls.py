# Copyright 2015 Lenovo
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.conf.urls import patterns
from django.conf.urls import url

# from .views import IndexView, DeployView, DetailView, AssignsView, do_nothing
from openstack_dashboard.dashboards.admin.virtual_disks import views

urlpatterns = patterns('openstack_dashboard.dashboards.admin.virtual_disks.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<virtual_disk_id>[^/]+)/detail/$', views.DetailView.as_view(), name='detail'),
    url(r'^virtual_disk_info/(?P<virtual_disk_id>[^/]+)/$', views.GetOneVirtualDiskInfoView.as_view(), name='get_one_virtual_disk_info'),
    url(r'^refresh/$', views.RefreshView.as_view(), name='refresh'),
)

'''
url(r'^(?P<uuid>[^/]+)/deploy/$', views.DeployView.as_view(), name='deploy'),
url(r'^assigns/$', views.AssignsView.as_view(), name='assigns'),
url(r'^(?P<uuid>[^/]+)/associate_auth/$', views.AssociateAuthView.as_view(), name='associate_auth'),
url(r'^add/$', views.AddView.as_view(), name='add'),
url(r'^(?P<uuid>[^/]+)/editserver/$', views.EditView.as_view(), name='editserver'),
url(r'^manage/$', views.ManageView.as_view(), name='manage'),
url(r'^(?P<id>[^/]+)/edit_xclarity/$', views.EditXClarityView.as_view(), name='edit_xclarity'),
url(r'^(?P<uuid>[^/]+)/detail/$', views.DetailView.as_view(), name='detail'),
url(r'^(?P<uuid>[^/]+)/readycheck/$', views.CheckView.as_view(), name='readycheck'),
url(r'^config/$', views.ConfigView.as_view(), name='config'),
url(r'^(?P<uuid>[^/]+)/hypervizor/$', views.HypervisorView.as_view(), name='hypervizor'),
url(r'^refresh/$', views.RefreshView.as_view(), name='refresh'),
url(r'^refresh_approval/$', views.RefreshApprovalView.as_view(), name='refresh_approval'),
#url(r'^nosuch', views.do_nothing, name='nosuch'),
'''

