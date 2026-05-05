def run(context):
    logger = context["logger"]
    logger.info("Executando rotina de layout.")
    return {
        "status": "ok",
        "message": "Layout processado com sucesso.",
        "args_recebidos": context.get("args_list", []),
        "script": context.get("script_name"),
    }
