def main(context):
    logger = context["logger"]
    logger.info("Atualizando dashboard de exemplo.")
    selected = context.get("selected_scripts", [])
    return {
        "status": "ok",
        "message": "Dashboard atualizado.",
        "scripts_selecionados": selected,
    }
