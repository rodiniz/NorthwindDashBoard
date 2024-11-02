import reflex as rx

styles = {
    "card": {
        "background": "white",
        "padding": "2em",
        "border_radius": "lg",
        "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "width": "100%",
        "max_width": "500px",
    },
    "input": {
        "border": "1px solid #E2E8F0",
        "padding": "0.5em",
        "border_radius": "md",
        "width": "100%",
        "margin_bottom": "1em"
        
    },
    "button": {
        "width": "100%",
        "padding": "0.5em",
        "border_radius": "md",
        "background": "rgb(59, 130, 246)",
        "color": "white",
        "font_weight": "bold",
        "margin": "1em 0",
        "_hover": {
            "background": "rgb(37, 99, 235)",
        }
    },
    "error": {
        "background": "rgb(254, 242, 242)",
        "color": "rgb(153, 27, 27)",
        "padding": "1em",
        "border_radius": "md",
        "margin_bottom": "1em",
        "width": "100%",
    },
    "link": {
        "color": "rgb(59, 130, 246)",
        "text_decoration": "none",
        "_hover": {
            "text_decoration": "underline",
        }
    }
}

class State(rx.State):
  
    error: str = ""
    
    def login(self, form_data:dict):
        if not form_data['email'] or not form_data['password']:
            self.error = "Por favor, preencha todos os campos"
            return
        
        if "@" not in form_data['email']:
            self.error = "Por favor, insira um email válido"
            return
            
       
        self.error = ""
        print(f"Tentativa de login com: {form_data}")

def login_card():
    return rx.card(
                rx.form(
                    rx.vstack(
                        rx.heading("Login", size="lg", text_align="center"),        
                    
                        rx.cond(
                            State.error != "",
                            rx.box(
                                State.error,                
                                width="100%",
                                style=styles["error"]
                            ),
                        ),
                    
                    rx.vstack(
                        rx.text(
                            "Email address",
                            size="3",
                            weight="medium",
                            text_align="left",
                            width="100%",
                        ),
                        rx.input(
                            placeholder="user@reflex.dev",
                            type="email",
                            size="3",
                            width="100%",
                            name="email"
                          
                        ),
                        justify="start",
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                "Password",
                                size="3",
                                weight="medium",
                            ),
                            rx.link(
                                "Forgot password?",
                                href="#",
                                size="3",
                            ),
                            justify="between",
                            width="100%",
                        ),
                    rx.input(
                        placeholder="Enter your password",
                        type="password",
                        size="3",
                        width="100%",
                        name="password"
                       
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Entrar",                   
                    width="100%",
                    style=styles["button"],
                    type="submit"
                   
                ),                
           
                rx.hstack(
                    rx.link("Esqueceu sua senha?", color="blue.500"),
                    rx.spacer(),
                    rx.link("Registre-se", color="blue.500"),
                    width="100%",
                ),
            
                spacing="4",
            
                padding="6",
                bg="white",
        
            ),
            on_submit=State.login,
            reset_on_submit=True
         ),
        style=styles['card']
   )
@rx.page(route="/settings", title="Settings")
def settings():
    return rx.center(
        login_card(),
        width="100%",
        min_height="60vh",
        bg="gray.50",
    )