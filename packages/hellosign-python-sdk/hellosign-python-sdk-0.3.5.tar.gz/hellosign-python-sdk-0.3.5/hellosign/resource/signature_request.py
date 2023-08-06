from resource import Resource


class SignatureRequest(Resource):

    """Contains information regarding documents that need to be signed

    Comprises the following attributes:

        test_mode (bool): Whether this is a test signature request. Test
            requests have no legal value. Defaults to 0.

        signature_request_id (str): The id of the SignatureRequest

        requester_email_address (str): The email address of the initiator of
            the SignatureRequest

        title (str): The title the specified Account uses for the
            SignatureRequest

        subject (str): The subject in the email that was initially sent to the
            signers

        message (str): The custom message in the email that was initially sent
            to the signers

        is_complete (bool): Whether or not the SignatureRequest has been fully
            executed by all signers

        has_error (bool): Whether or not an error occurred (either during the
            creation of the SignatureRequest or during one of the signings)

        final_copy_uri (DEPRECATED): The relative URI where the PDF copy of the
            finalized documents can be downloaded. Only present when
            `is_complete = true`. This will be removed at some point; use the
            `files_url` instead

        files_url (str): The URL where a copy of the request's documents can be
            downloaded

        signing_url (str): The URL where a signer, after authenticating, can
            sign the documents

        details_url (str): The URL where the requester and the signers can view
            the current status of the SignatureRequest

        cc_email_addresses (list): A list of email addresses that were CCed on
            the SignatureRequest. They will receive a copy of the final PDF
            once all the signers have signed

        signing_redirect_url (str): The URL you want the signer redirected to
            after they successfully sign

        custom_fields (list of dict): An array of Custom Field objects
            containing the name and type of each custom field

            name (str): The name of the Custom Field
            type (str): The type of this Custom Field. Currently, `text` and
                `checkmark` are the only valid values

        response_data (list of dict): An array of form field objects containing
            the name, value, and type of each textbox or checkmark field filled
            in by the signers

            api_id (str): The unique ID for this field
            signature_id (str): The ID of the signature to which this response
                is linked
            name (str): The name of the form field
            value (str): The value of the form field
            type (str): The type of this form field

        signatures (list of dict): An array of signature obects, 1 for each
            signer

            signature_id (str): Signature identifier
            signer_email_address (str): The email address of the signer
            signer_name (str): The name of the signer
            order (str): If signer order is assigned this is the 0-based index
                for this signer
            status_code (str): The current status of the signature. eg:
                `awaiting_signature`, `signed`, `on_hold`
            signed_at (str): Time that the document was signed or null
            last_viewed_at (str): The time that the document was last viewed by
                this signer or null
            last_reminded_at (str): The time the last reminder email was sent
                to the signer or null
            has_pin (bool): Boolean to indicate whether this signature requires
                a PIN to access

    """
