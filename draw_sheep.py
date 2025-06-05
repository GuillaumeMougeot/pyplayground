import turtle

def draw_circle(t, radius, x, y, fill_color=None):
    t.penup()
    t.goto(x, y - radius)  # adjust starting point for circle drawing
    t.pendown()
    if fill_color:
        t.color("black", fill_color)
        t.begin_fill()
    else:
        t.color("black")
    t.circle(radius)
    if fill_color:
        t.end_fill()

def draw_head(t):
    # Draw the head as a small circle
    draw_circle(t, 20, -100, 50, fill_color="lightgray")
    # Draw the eye as a dot
    t.penup()
    t.goto(-115, 70)
    t.pendown()
    t.dot(5, "black")

def draw_body(t):
    # Draw the fluffy body as a larger circle
    draw_circle(t, 50, 0, 0, fill_color="white")

def draw_legs(t):
    # Define positions for four legs relative to the body
    leg_positions = [(20, -50), (0, -50), (-20, -50), (-40, -50)]
    t.color("black")
    for pos in leg_positions:
        t.penup()
        t.goto(pos)
        t.pendown()
        t.setheading(-90)  # point downwards
        t.forward(30)

def draw_sheep():
    screen = turtle.Screen()
    screen.title("ASCII Sheep to Turtle Sheep")
    t = turtle.Turtle()
    t.speed(2)

    # Draw body first
    draw_body(t)
    # Draw head
    draw_head(t)
    # Draw legs
    draw_legs(t)

    # Hide turtle and display window
    t.hideturtle()
    turtle.done()

if __name__ == '__main__':
    draw_sheep()
