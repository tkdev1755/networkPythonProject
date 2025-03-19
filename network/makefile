CC = gcc
CFLAGS = -Wall -Wextra 
SRC = networkEngine.c includes/networking.c
OBJ = $(SRC:.c=.o)
EXEC = networkEngine

all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(OBJ) -o $(EXEC)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ)

fclean: clean
	rm -f $(EXEC)

re: fclean all
