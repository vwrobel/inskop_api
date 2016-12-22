import sys
from django.core.management.base import BaseCommand
from cvtools import processes
import os.path, pkgutil
from inskop.code_manager.models import Code, CodeCategory
from inskop.account_manager.models import Auth0User
import importlib.util


class Command(BaseCommand):
    help = 'Creates codes in db from modules in cvtools'

    def handle(self, *args, **options):
        processes_path = os.path.dirname(processes.__file__)
        for _, process_type, _ in pkgutil.iter_modules([processes_path]):
            for _, process_name, _ in pkgutil.iter_modules([os.path.join(processes_path, process_type)]):
                code_category = CodeCategory.objects.get(name=process_type)
                staffOwner = Auth0User.objects.get(authorization__name='staff')
                try:
                    code = Code.objects.get(owner=staffOwner, category=code_category, name=process_name)
                except:
                    code = Code.objects.create(
                        owner=staffOwner,
                        category=code_category,
                        name=process_name,
                        active=True,
                        valid=True
                    )
                finally:
                    module_path = os.path.join(processes_path, process_type, process_name + '.py')
                    read_me_path = os.path.join(processes_path, process_type, process_name + '.md')
                    with open(module_path, 'r') as content_file:
                        code.code = content_file.read()
                    with open(read_me_path, 'r') as content_file:
                        code.read_me = content_file.read()

                    process_module = importlib.import_module('cvtools.cvtools.processes.' + process_type + '.' + process_name)
                    code.default_param = process_module.PARAM_DEFAULT
                    code.description = process_module.__doc__
                    code.save()
                    self.stdout.write(process_type + ' ' + process_name + ' created or updated')
