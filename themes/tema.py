from flet import colors, ButtonStyle, RoundedRectangleBorder

class AppTheme:
    # =====================
    # CORES - Tema Claro
    # =====================
    PRIMARY_COLOR = "#2E7D32"  # Verde escuro
    SECONDARY_COLOR = "#A5D6A7"  # Verde claro
    BACKGROUND_COLOR = "#F1F8E9"  # Verde muito claro
    TEXT_COLOR = "#212121"  # Quase preto
    TEXT_FIELD_COLOR = "#FFFFFF"
    FIELD_BG_COLOR = "#FFFFFF"
    ICON_COLOR = "#c3fac6"
    WARNING_TEXT_COLOR = "#FF5722"
    AMARELO_COLOR = "#787840"
    ACCENT_COLOR = "#FF7043"

    # Botões
    BUTTON_BG_COLOR = "#6E8C75"
    BUTTON_BG_COLOR_DISABLED = "#BFD2C3"
    BUTTON_COLOR_TEXT = "#FFFFFF"
    BUTTON_COLOR_TEXT_DISABLED = "#2E7D32"
    MEN_BUTTON_COLOR = "#A5D6A7"
    WOMAN_BUTTON_COLOR = "#ffa07a"
    VOLTAR_COLLOR_BUTTON = "#799266"

    # Chips
    CHIP_ICON_COLOR = "#2E7D32"
    CHIP_TEXT_COLOR = "#4a4a28"
    CHIP_GRADIENT_UNSELECTED_1 = "#DCECC9"
    CHIP_GRADIENT_UNSELECTED_2 = "#B5D99C"
    CHIP_GRADIENT_SELECTED_1 = "#8BC34A"
    CHIP_GRADIENT_SELECTED_2 = "#689F38"
    CHIP_GRADIENT_ERROR_1 = "#FDDEDE"
    CHIP_GRADIENT_ERROR_2 = "#FABCBC"
    CHIP_PREF_ALIM_COLOR = "#799266"
    CHIP_PREF_ALIM_COLOR_SELECTED = "#9ba891"

    # Barra de progresso
    PROCESSBAR_COLOR = "#A5D6A7"

    # =====================
    # CORES - Tema Escuro (comentado)
    # =====================
    # DARK_BACKGROUND_COLOR = "#121212"
    # DARK_SURFACE_COLOR = "#1E1E1E"
    # DARK_TEXT_COLOR = "#DCDCDC"
    # DARK_CARD_COLOR = "#2C2C2C"
    # DARK_FIELD_COLOR = "#2C2C2C"
    # DARK_BUTTON_COLOR = "#388E3C"
    # DARK_BUTTON_TEXT_COLOR = "#FFFFFF"
    # DARK_WARNING_TEXT_COLOR = "#FFAB91"
    # DARK_TEXT_FIELD_COLOR = "#2C2C2C"

    # =====================
    # LAYOUT E ESTILO
    # =====================
    PADDING = 16
    BORDER_RADIUS = 8
    BUTTON_BORDER_RADIUS = 20

    @staticmethod
    def get_color(name):
        """Retorna cor fixa independente do tema"""
        return getattr(AppTheme, name, "#000000")

    @staticmethod
    def get_color_by_mode(name, is_dark_mode: bool):
        """
        Busca cor clara ou escura com base no modo atual.
        Ex: get_color_by_mode("TEXT_COLOR", is_dark)
        """
        # 🔥 Comentado suporte ao modo escuro
        # if is_dark_mode:
        #     dark_variant = f"DARK_{name}"
        #     return getattr(AppTheme, dark_variant, getattr(AppTheme, name, "#000000"))
        return getattr(AppTheme, name, "#000000")

    @staticmethod
    def get_title_style(is_dark=False):
        return {
            "size": 24,
            "weight": "bold",
            # 🔥 Sempre cor clara
            "color": AppTheme.get_color("TEXT_COLOR")
        }

    @staticmethod
    def get_label_style(is_dark=False):
        return {
            "size": 16,
            "color": AppTheme.get_color("TEXT_COLOR")
        }

    @staticmethod
    def get_helper_style(is_dark=False):
        return {
            "size": 12,
            "italic": True,
            "color": AppTheme.get_color("TEXT_COLOR")
        }

    @staticmethod
    def button_style(color):
        return ButtonStyle(
            bgcolor=color,
            shape=RoundedRectangleBorder(radius=AppTheme.BUTTON_BORDER_RADIUS)
        )
