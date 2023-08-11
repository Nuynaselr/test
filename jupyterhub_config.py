import os
import re
import sys
from traitlets import Unicode
from jupyterhub.utils import url_path_join
from jupyterhub.handlers.login import LogoutHandler
from tornado.httputil import url_concat
from ldap3 import Server, Connection, ALL
from bs4 import BeautifulSoup
from kubespawner import KubeSpawner
from oauthenticator.generic import GenericOAuthenticator

class KeycloakLogoutHandler(LogoutHandler):
    """Logout handler for keycloak"""

    async def render_logout_page(self):
        params = {
            'redirect_uri': '%s://%s%s' % (
                self.request.protocol,
                self.request.host,
                self.hub.server.base_url),
            }
        self.redirect(
            url_concat(self.authenticator.keycloak_logout_url, params),
            permanent=False
        )

class KeycloakAuthenticator(GenericOAuthenticator):
    """Authenticator handling keycloak logout"""

    keycloak_logout_url = Unicode(
        config=True,
        help="The keycloak logout URL"
    )

    def get_handlers(self, app):
        return super().get_handlers(app) + [(r'/logout', KeycloakLogoutHandler)]




notebook_images = {
        
        }



## Ldap params configuration
ad_address = 
search_user = 
search_password = 
user_search_base = 
admin_group = 

## Ldap groups that can auth in jupyterhub (you can add more groups, but available list cpu and ram is 1 core and 4 GB)
ad_groups = [
    admin_group
    ]

## List of number of cores available for admin and ds group from ldap
admin_cpu_lst = [4,8,16,24,32]

## List of ram in GB available for admin and ds group from ldap
admin_ram_lst = [4,8,16,32,64,128,256]

## List of ram in GB available for admin and ds group from ldap
admin_gpu_lst = [0,1]


c.JupyterHub.authenticator_class = KeycloakAuthenticator
c.KeycloakAuthenticator.keycloak_logout_url = 
c.GenericOAuthenticator.login_service = "keycloak"
c.OAuthenticator.client_id = ""
c.OAuthenticator.client_secret = 
c.GenericOAuthenticator.authorize_url = 
c.GenericOAuthenticator.oauth_callback_url = 
c.GenericOAuthenticator.userdata_url = 
c.GenericOAuthenticator.token_url = 
c.GenericOAuthenticator.userdata_method = 'GET'
c.GenericOAuthenticator.userdata_params = {"state": "state"}
c.GenericOAuthenticator.username_key = "preferred_username"
c.OAuthenticator.tls_verify = False
c.Authenticator.auto_login = True
c.Authenticator.logout_url = 
c.JupyterHub.logout_url = 
c.GenericOAuthenticator.logout_redirect_url = 
c.OAuthenticator.logout_redirect_url = 
c.JupyterHub.shutdown_on_logout = True

#c.Spawner.environment = {}

# c.KubeSpawner.extra_container_config = {
#     "envFrom": [{
#         "secretRef": {
#             "name": "gitlab-craete-project"
#         }
#     }]
# }



class Spawner(KubeSpawner):
    def _options_form_default(self):
        username = self.user.name
        group_lst = getadgroup(username, ad_address, search_user, search_password, user_search_base, ad_groups)

        soup = BeautifulSoup(f"""
            <label for="stack">{username}, выберете желаемый стек: </label>
            <select name="stack" size="1">
            </select><br>
            <label for="cpu">Выберете желаемое количество ядер: </label>
            <select name="cpu" size="1">
            </select><br>
            <label for="memory">Выберете желаемое количество оперативной памяти: </label>
            <select name="memory" size="1">
            </select><br>
            <label for="gpu">Выберете желаемое количество gpu: </label>
            <select name="gpu" size="1">
            </select>
            """)

        for item in soup.find_all('select', {"name": "stack"}):
            notebooks = ''
            for k, v in notebook_images.items():
                    notebooks += f'<option value="{k}">{v}</option>'
            tags = BeautifulSoup(notebooks)
            item.append(tags)

        for item in soup.find_all('select', {"name": "cpu"}):
            if admin_group in group_lst:
                cpu_lst = ''
                for i in admin_cpu_lst:
                    cpu_lst += f'<option value="{i}">{i} Core</option>'
                tags = BeautifulSoup(cpu_lst)
                item.append(tags)
            elif admin_group not in group_lst:
                cpu_lst = ''
                if ds_lead_group in group_lst:
                    for i in ds_lead_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif ds_group in group_lst:
                    for i in ds_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif analyst_group in group_lst:
                    for i in analyst_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif ds_s_group in group_lst:
                    for i in ds_s_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif infosec_group in group_lst:
                    for i in infosec_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
            else:
                tags = BeautifulSoup('<option value="1">1 Core</option>')
                item.append(tags)

        for item in soup.find_all('select', {"name": "memory"}):
            if admin_group in group_lst:
                ram_lst = ''
                for i in admin_ram_lst:
                    ram_lst += f'<option value="{i}G">{i} GB</option>'
                tags = BeautifulSoup(ram_lst)
                item.append(tags)
            elif admin_group not in group_lst:
                ram_lst = ''
                if ds_lead_group in group_lst:
                    for i in ds_lead_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif ds_group in group_lst:
                    for i in ds_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif analyst_group in group_lst:
                    for i in analyst_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif ds_s_group in group_lst:
                    for i in ds_s_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif infosec_group in group_lst:
                    for i in infosec_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
            else:
                tags = BeautifulSoup('<option value="4G">4 GB</option>')
                item.append(tags)

        for item in soup.find_all('select', {"name": "gpu"}):
            if admin_group in group_lst:
                gpu_lst = ''
                for i in admin_gpu_lst:
                    gpu_lst += f'<option value="{i}">{i} count</option>'
                tags = BeautifulSoup(gpu_lst)
                item.append(tags)
            elif admin_group not in group_lst:
                gpu_lst = ''
                if ds_lead_group in group_lst:
                    for i in ds_lead_gpu_lst:
                        gpu_lst += f'<option value="{i}">{i} count</option>'
                    tags = BeautifulSoup(gpu_lst)
                    item.append(tags)
                elif ds_group in group_lst:
                    for i in ds_gpu_lst:
                        gpu_lst += f'<option value="{i}">{i} count</option>'
                    tags = BeautifulSoup(gpu_lst)
                    item.append(tags)
                elif analyst_group in group_lst:
                    for i in analyst_gpu_lst:
                        gpu_lst += f'<option value="{i}">{i} count</option>'
                    tags = BeautifulSoup(gpu_lst)
                    item.append(tags)
                elif ds_s_group in group_lst:
                    for i in ds_s_gpu_lst:
                        gpu_lst += f'<option value="{i}">{i} count</option>'
                    tags = BeautifulSoup(gpu_lst)
                    item.append(tags)
                elif infosec_group in group_lst:
                    for i in infosec_gpu_lst:
                        gpu_lst += f'<option value="{i}">{i} count</option>'
                    tags = BeautifulSoup(gpu_lst)
                    item.append(tags)
            else:
                tags = BeautifulSoup('<option value="0">0 count</option>')
                item.append(tags)
        return str(soup)


    def options_from_form(self, formdata):
        options = {}
        options['stack'] = formdata['stack']
        container_image = ''.join(formdata['stack'])
        print("SPAWN: " + container_image + " IMAGE")
        self.image = container_image
        options = {}
        options['gpu'] = formdata['gpu']
        container_gpu = ''.join(formdata['gpu'])
        print("SPAWN: " + container_gpu + " gpu")
        self.extra_resource_limits = {"nvidia.com/gpu": container_gpu}
        options = {}
        options['cpu'] = formdata['cpu']
        container_cpu = ''.join(formdata['cpu'])
        print("SPAWN: " + container_cpu + " cpu")
        self.cpu_limit = float(container_cpu)
        options = {}
        options['memory'] = formdata['memory']
        container_memory = ''.join(formdata['memory'])
        print("SPAWN: " + container_memory + " memory")
        self.mem_limit = container_memory
        return options
        
def getadgroup(username, ad_server, search_user, search_password, user_search_base, ad_groups):
    server = Server(ad_server, get_info=ALL)

    conn = Connection(server, search_user, search_password, auto_bind=True)
    conn.search(user_search_base, '(&(objectclass=person)(sAMAccountName='+username+'))', attributes=['memberof'])
    group_list=list(conn.entries[0].memberof)

    return group_list

c.JupyterHub.spawner_class = Spawner

# Connect to a proxy running in a different pod
# c.ConfigurableHTTPProxy.api_url = 'http://{}:{}'.format(os.environ['PROXY_API_SERVICE_HOST'], int(os.environ['PROXY_API_SERVICE_PORT']))
c.ConfigurableHTTPProxy.should_start = True

# # Do not shut down user pods when hub is restarted
# c.JupyterHub.cleanup_servers = False

# # Check that the proxy has routes appropriately setup
c.JupyterHub.last_activity_interval = 60


c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081
c.JupyterHub.port = 8000

# # Gives spawned containers access to the API of the hub
c.JupyterHub.hub_connect_ip = 'hub'

c.KubeSpawner.namespace = 'dev'

c.KubeSpawner.image = "jupyter/pyspark-notebook:latest"

c.KubeSpawner.service_account = "hub"
c.KubeSpawner.start_timeout = 500

c.KubeSpawner.ip = '0.0.0.0'

# Mount volume for storage
pvc_name_template = 'claim-{username}'
c.KubeSpawner.pvc_name_template = pvc_name_template
volume_name_template = 'volume-{username}'

c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.storage_class = 'glusterfs'
c.KubeSpawner.storage_access_modes = ['ReadWriteOnce']
c.KubeSpawner.storage_capacity = '10Gi'

# Add volumes to singleuser pods
c.KubeSpawner.volumes = [
    {
        'name': volume_name_template,
        'persistentVolumeClaim': {
            'claimName': pvc_name_template
        }
    },
    {
        'name': 'claim-share',
        'persistentVolumeClaim': {
            'claimName': 'claim-share'
        }
    }
]
c.KubeSpawner.volume_mounts = [
    {
        'mountPath': '/home/jovyan',
        'name': volume_name_template
    },
    {
        'mountPath': '/home/jovyan/share',
        'name': 'claim-share'
    }
]

# # Add /home/jovyan/.ssh and chmod 600
c.KubeSpawner.lifecycle_hooks = {
    "postStart": {
        "exec": {
            "command": ["/bin/sh", "-c", "mkdir -p /home/jovyan/.ssh --mode=700; if [[ -L ~/snippets ]]; then echo 'Snippets link already exists. Skip.'; else ln -s ~/share/snippets ~/snippets; fi; rm -rf ~/share/snippets/snippets"]
        }
    }
}

c.NotebookApp.certfile = u'/etc/jupyterhub/cert/example.cert'
c.NotebookApp.keyfile = u'/etc/jupyterhub/key/example.key'

# c.Authenticator.whitelist = {'admin'}
c.JupyterHub.admin_access = True
c.Spawner.cmd=['jupyter-labhub']
