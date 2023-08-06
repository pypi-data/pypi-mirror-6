from Products.Archetypes.interfaces.field import IField
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFCore.Expression import getExprContext
from wildcard.pfg.stripe.interfaces import IStripeField
import requests
import logging

logger = logging.getLogger('wildcard.pfg.stripe')


def fgProcessActionAdapters(self, errors, fields=None, REQUEST=None):
    if fields is None:
        fields = [fo for fo in self._getFieldObjects()
                  if not IField.providedBy(fo)]

    if not errors:
        if self.getRawAfterValidationOverride():
            # evaluate the override.
            # In case we end up traversing to a template,
            # we need to make sure we don't clobber
            # the expression context.
            self.getAfterValidationOverride()
            self.cleanExpressionContext(request=self.REQUEST)

        # get a list of adapters with no duplicates, retaining order
        adapters = []
        for adapter in self.getRawActionAdapter():
            if adapter not in adapters:
                adapters.append(adapter)

        for adapter in adapters:
            actionAdapter = getattr(self.aq_explicit, adapter, None)
            if actionAdapter is None:
                logger.warn(
                    "Designated action adapter '%s' is missing; ignored. "
                    "Removing it from active list." %
                    adapter)
                self.toggleActionActive(adapter)
            else:
                # Now, see if we should execute it.
                # Check to see if execCondition exists and has contents
                if safe_hasattr(actionAdapter, 'execCondition') and \
                        len(actionAdapter.getRawExecCondition()):
                    # evaluate the execCondition.
                    # create a context for expression evaluation
                    context = getExprContext(self, actionAdapter)
                    doit = actionAdapter.getExecCondition(
                        expression_context=context)
                else:
                    # no reason not to go ahead
                    doit = True

                if doit:
                    result = actionAdapter.onSuccess(fields,
                                                     REQUEST=REQUEST)
                    if type(result) is type({}) and len(result):
                        # return the dict, which hopefully uses
                        # field ids or FORM_ERROR_MARKER for keys
                        return result
        # see if there is a stripe field
        fields = [fo for fo in self._getFieldObjects()
                  if IStripeField.providedBy(fo)]

        for field in fields:
            name = field.fgField.getName()
            value = REQUEST.form[name]
            resp = requests.post(
                'https://api.stripe.com/v1/charges',
                auth=(field.getStripeSecretKey(), ''),
                data={
                    'amount': value['amount'],
                    'currency': field.getStripeCurrency(),
                    'card': value['token']
                }
            )
            try:
                data = resp.json()
                if 'error' in data:
                    errors[name] = 'Stripe API Errror: %s' % (
                        data['error']['message'])
            except:
                errors[name] = 'Error processing charge'
    return errors
