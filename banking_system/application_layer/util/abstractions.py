def save_transaction(account_repository, transaction_repository, notification_service, logging_service, account, transaction):
    # update the account balance and save the transaction
    account_repository.update_account(account)
    transaction_repository.save_transaction(transaction)

    # Notify and log the transaction
    notification_service.notify(transaction)
    logging_service.log_transaction(transaction)

    return transaction
