# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError


class CamtParser(models.AbstractModel):
    """Parser for camt bank statement import files."""

    _inherit = "account.statement.import.camt.parser"

    def parse_statement(self, ns, node):
        statement = super().parse_statement(ns, node)
        if node.tag == f"{{{ns}}}Ntfctn":
            statement.setdefault("creation_context", {})["camt54_notification"] = True
        return statement

    def _get_partner_ref(self, isr):
        ICP = self.env["ir.config_parameter"]
        ref_format = ICP.sudo().get_param("qrr_partner_ref")
        if not ref_format:
            return
        config = ref_format.split(",")
        if len(config) == 2:
            start, size = config
        elif len(config) == 1:
            start = config[0]
            size = 6
        else:
            raise UserError(
                self.env._(
                    "Config parameter `qrr_partner_ref` is wrong.\n"
                    "It must be in format `i[,n]` \n"
                    "where `i` is the position of the first digit and\n"
                    "`n` the number of digit in the reference,"
                    " by default 6.\n"
                    'e.g. "13,6"'
                )
            )
        try:
            start = int(start) - 1  # count from 1 instead of 0
            size = int(size)
            end = start + size
        except ValueError:
            raise UserError(
                self.env._(
                    "Config parameter `qrr_partner_ref` is wrong.\n"
                    "It must be in format `i[,n]` \n"
                    "`i` and `n` must be integers.\n"
                    'e.g. "13,6"'
                )
            ) from None
        return isr[start:end].lstrip("0")

    def parse_transaction_details(self, ns, node, transaction):
        """Put ESR in label and add aditional information to label
        if no esr is available
        """
        super().parse_transaction_details(ns, node, transaction)
        # put the esr in the label. odoo reconciles based on the label,
        # if there is no esr it tries to use the information textfield

        references = {}
        self.add_value_from_node(
            ns, node, "./ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref", references, "qrr"
        )
        qrr_number = references.get("qrr")
        if qrr_number:
            transaction["payment_ref"] = qrr_number
            partner_ref = self._get_partner_ref(qrr_number)
            if partner_ref:
                transaction["partner_ref"] = partner_ref
        else:
            label_paths = [
                "./ns:RmtInf/ns:Ustrd|./ns:RtrInf/ns:AddtlInf",
                "./ns:AddtlNtryInf",
            ]
            if node.xpath("ancestor::ns:Ntfctn", namespaces={"ns": ns}):
                label_paths.append("./ns:Refs/ns:InstrId")
            self.add_value_from_node(ns, node, label_paths, transaction, "payment_ref")
            self.add_value_from_node(
                ns, node, "../../ns:AcctSvcrRef", references, "servicer"
            )
            trans_id = references.get("servicer")
            if trans_id:
                payment_ref = transaction.get("payment_ref")
                transaction["payment_ref"] = (
                    f"{payment_ref} ({trans_id})" if payment_ref else trans_id
                )
        # End add esr to the label.

        # add transaction id to ref
        self.add_value_from_node(
            ns,
            node,
            [
                "./../../ns:AcctSvcrRef",
                "./ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref",
                "./ns:Refs/ns:EndToEndId",
            ],
            transaction,
            "ref",
        )
        return True
