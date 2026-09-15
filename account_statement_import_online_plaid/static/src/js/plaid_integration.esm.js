/** @odoo-module **/
/* global Plaid */
import {registry} from "@web/core/registry";

export async function plaid_login(env, action) {
    const handler = Plaid.create({
        onSuccess: (public_token, metadata) => {
            env.services.orm.call(action.params.call_model, action.params.call_method, [
                public_token,
                action.params.object_id,
                metadata.accounts,
            ]);
        },

        token: action.params.token,
    });
    handler.open();
}

registry.category("actions").add("plaid_login", plaid_login);
