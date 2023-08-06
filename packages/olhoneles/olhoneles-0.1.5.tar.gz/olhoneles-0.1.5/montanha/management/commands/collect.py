# -*- coding: utf-8 -*-
#
# Copyright (©) 2010-2014 Gustavo Noronha Silva
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import signal
import sys

# This hack makes django less memory hungry (it caches queries when running
# with debug enabled.
from django.conf import settings
settings.DEBUG = False

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from montanha.models import Expense


debug_enabled = False


class Command(BaseCommand):
    args = "<source> [debug]"
    help = "Collects data for a number of sources"

    @transaction.commit_on_success
    def handle(self, *args, **options):
        global debug_enabled

        settings.expense_locked_for_collection = True

        collection_runs = []

        debug_enabled = False
        if "debug" in args:
            debug_enabled = True

        def signal_handler(signal, frame):
            transaction.rollback()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        houses_to_consolidate = []

        try:
            if "almg" in args:
                from almg import ALMG
                almg = ALMG(collection_runs, debug_enabled)
                almg.update_legislators()
                almg.update_data()
                almg.update_legislators_data()
                houses_to_consolidate.append("almg")

            if "senado" in args:
                from senado import Senado
                senado = Senado(collection_runs, debug_enabled)
                senado.update_legislators()
                senado.update_data()
                senado.update_legislators_extra_data()
                houses_to_consolidate.append("senado")

            if "cmbh" in args:
                from cmbh import CMBH
                cmbh = CMBH(collection_runs, debug_enabled)
                cmbh.update_legislators()
                cmbh.update_data()
                houses_to_consolidate.append("cmbh")

            if "cmsp" in args:
                from cmsp import CMSP
                cmsp = CMSP(collection_runs, debug_enabled)
                cmsp.update_data()
                houses_to_consolidate.append("cmsp")

            if "camarafederal" in args:
                from camarafederal import CamaraFederal
                camarafederal = CamaraFederal(collection_runs, debug_enabled)
                args = args[1:]

                if args[0] == "legislatures":
                    camarafederal.collect_legislatures()

                if args[0] == "legislators":
                    camarafederal.collect_legislators()

                if args[0] == "expenses":
                    camarafederal.collect_expenses()
                houses_to_consolidate.append("camarafederal")

            if "cdep" in args:
                from cdep import CamaraDosDeputados
                cdep = CamaraDosDeputados(collection_runs, debug_enabled)
                cdep.update_legislators()
                cdep.update_data()
                houses_to_consolidate.append("camarafederal")

            settings.expense_locked_for_collection = False

            for run in collection_runs:
                legislature = run.legislature
                Expense.objects.filter(mandate__legislature=legislature).delete()

                columns = "number, nature_id, date, value, expensed, mandate_id, supplier_id"

                cursor = connection.cursor()
                cursor.execute("insert into montanha_expense (%s) select %s from montanha_archivedexpense where collection_run_id=%d" % (columns, columns, run.id))
                cursor.close()

                # FIXME: this is not required in django 1.6.
                transaction.commit_unless_managed()

        except Exception:
            transaction.rollback()
            raise

        transaction.commit()

        for house in houses_to_consolidate:
            call_command("consolidate", house)
