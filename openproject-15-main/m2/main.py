import numpy as np
import sys
import os
import argparse
import cv2
from skimage import io, color, img_as_ubyte


# 0 Up
# 1 Left
# 2 Down
# 3 Right
P = 0.3
Q = 0.0625

def difference(x_i, x_j, relation):
    nrows, ncols = x_i.shape[0], x_i.shape[1]

    if relation == 1:
        return difference(x_j, x_i, 3)
    elif relation == 3:
        return np.sum(
            np.power(np.power(np.abs((2 * x_i[:, ncols - 1] - x_i[:, ncols - 2]) - x_j[:, 0]), P) +
                     np.power(np.abs((2 * x_j[:, 0] - x_j[:, 1]) - x_i[:, ncols - 1]), P), Q / P))
    elif relation == 0:
        return difference(x_j, x_i, 2)
    elif relation == 2 :
        return np.sum(
            np.power(np.power(np.abs((2 * x_i[nrows - 1] - x_i[nrows - 2]) - x_j[0]), P) +
                     np.power(np.abs((2 * x_j[0] - x_j[1]) - x_i[nrows - 1]), P), Q / P))
    else:
        raise TypeError(f'invalid relation: {relation}')



# def difference(square_i, square_j, k):
#     P = 0.3
#     Q = 0.0625
#     M, N , C = square_i.shape
#     if k == 0: ## square_j above square_i
#         return  np.sum(np.power(np.power(np.abs((2 * square_j[M - 1] - square_j[M - 2]) - square_i[0]), P) +
#                      np.power(np.abs((2 * square_i[0] - square_i[1]) - square_j[M - 1]), P), Q / P))
#     elif k == 1: ## square_j right of square_i
#         return np.sum(np.power(np.power(np.abs((2 * square_i[:, N - 1] - square_i[:, N - 2]) - square_j[:, 0]), P) +
#                      np.power(np.abs((2 * square_j[:, 0] - square_j[:, 1]) - square_i[:, N - 1]), P), Q / P))
#     elif k == 2: ## square_j below square_i
#         return  np.sum(np.power(np.power(np.abs((2 * square_i[M - 1] - square_i[M - 2]) - square_j[0]), P) +
#                      np.power(np.abs((2 * square_j[0] - square_j[1]) - square_i[M - 1]), P), Q / P))
#
#     elif k == 3: ## square_j left of square_i
#         return np.sum(np.power(np.power(np.abs((2 * square_j[:, N - 1] - square_j[:, N - 2]) - square_i[:, 0]), P) +
#                      np.power(np.abs((2 * square_i[:, 0] - square_i[:, 1]) - square_j[:, N - 1]), P), Q / P))
#     else:
#         exit(1)

def adjacent(x, y):
    return [(x-1, y), (x, y+1), (x+1,y), (x, y-1)]

def move(direction, i, j):
    if direction == 0:
        x, y = i - 1, j
    if direction == 1:
        x, y = i , j + 1
    if direction == 2:
        x, y = i + 1, j
    if direction == 3:
        x, y = i , j - 1

    return x, y

def filled(answer, x, y):
    i, j = answer.shape
    if x >= 0 and x < i and y >= 0 and y < j and answer[x][y] >= 0:
        return True
    else:
        return False

def fit(answer, best, candidate, part):
    i, j = candidate
    for k in range(4):
        x, y = move(k, i, j )
        if filled(answer, x, y):
            if not (best[k][i] == j and best[2 - k][j]  == i):
                return False
    
    return True

def average_compatability(answer, compatability, slot, part):
    i, j = slot
    num = 0
    total = 0
    for k in range(4):
        x,y = move(k, i, j)
        if filled(answer, x, y):
            total += compatability[k][part][answer[x][y]]
            num += 1
    if num == 0:
        return -1
    return total / num

def assign(answer, slot, part, remaining):
    M, N = answer.shape
    i, j = slot

    if i < 0:
        print("down")
        if np.any(answer[-1, :] >= 0):
            print("error move")
            raise("ERROR")
        answer = np.roll(answer, 1, 0)
        i += 1

    elif i >= M:
        print("Up")
        if np.any(answer[0] >= 0):
            print("error move")
            raise("ERROR")
        answer = np.roll(answer, -1, 0)
        i -= 1

    elif j < 0:
        print("right")
        if np.any(answer[:, -1] >= 0):
            print("error move")
            raise("ERROR")
        answer = np.roll(answer, 1, 1)
        j += 1

    elif j >= M:
        print("left")
        if np.any(answer[:, 0] >= 0):
            print("error move")
            raise("ERROR")
        answer = np.roll(answer, -1, 1)
        j -= 1

    remaining.remove(part)
    answer[i][j] = part
    return answer, remaining;


        

def place(answer, compatability, best, remaining, squares):
    l = len(remaining)
    while remaining:
        added = {}
        for x in range(len(answer)):
            for y in range(len(answer[0])):
                if answer[x][y] == -1:
                    continue
                else:
                    for i, j in adjacent(x, y):
                        if (i, j) in added:
                            continue
                        if  filled(answer, i, j):
                            continue
                        added[(i, j)] = sum(1 if filled(answer, p, q) else 0 for p, q in adjacent(i, j))
        max_neighbour = max(added.values())
        candidates = set(a for a, num in added.items() if num == max_neighbour)

        while True:
            matches = [(candidate, part) for candidate in candidates for part in remaining if fit(answer, best, candidate, part)]
            if len(matches) == 1:
                slot, part = matches.pop()
            else:
                average = [(average_compatability(answer, compatability, slot, part), (slot, part)) for slot in candidates for part in remaining ]
                best_possible = max(average, key = lambda x: x[0])
                slot, part = best_possible[1]

            try:
                show_image(answer, squares, answer.shape[0] * squares[0].shape[0], answer.shape[1] * squares[0].shape[1])
                answer, remaining = assign(answer, slot, part, remaining)
                break
            except Exception as e:
                print("error")
                candidates.remove(slot)
                if not candidates:
                    raise ValueError("no more slots")
    return answer

def better_show(name, image):
    cv2.imshow(name, image)
    while True:
        if cv2.waitKey(1) == ord('q'):
            break

        if cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE ) < 1:
            break


def show_image(answer, squares, M, N):
    image = np.zeros((M, N, 3))
    i, j = answer.shape
    squareheight, squarewidth, _ = squares[0].shape
    for x in range(i):
        for y in range(j):
            if answer[x][y] == -1:
                continue;
            else:
                image[x * squareheight: (x+1)*squareheight, y*squarewidth: (y+1)*squarewidth, :] = squares[answer[x][y]]
                # better_show("bye", squares[answer[x][y]])
                # better_show("bye", image[x * squareheight: (x+1)*squareheight, y*squarewidth: (y+1)*squarewidth, :])

    image = color.lab2rgb(image)
    image = img_as_ubyte(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    better_show("hello", image)

def calculate_score(answer, best):
    M, N = answer.shape
    num = 0

    for i in range(M):
        for j in range(N):
            if j < N - 1:
                if best[1][answer[i][j]] == answer[i][j+1] and best[3][answer[i][j+1]] == answer[i][j]:
                    num+=1
            if i < M - 1:
                if best[0][answer[i][j]] == answer[i+1][j] and best[2][answer[i+1][j]] == answer[i][j]:
                    num+=1

    return num / ((M - 1) * N + M * (N - 1))

def solve(image_name, rows, cols):
    # image = cv2.imread(image_name)
    image = io.imread(image_name)

    image = color.rgb2lab(image)
    M, N, _ = image.shape
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    squares = []
    pieceHeight = int(M / rows)
    pieceWidth = int(N / cols)

    for row in range(rows):
        for col in range(cols):
            squares.append(image[row * pieceHeight: (row + 1) * pieceHeight, col*pieceWidth : (col + 1) * pieceWidth, :])


    # for square in squares:
    #     cv2.imshow("hello", square)
    #     cv2.waitKey()

    dissimilarity = np.empty((4, len(squares), len(squares)))
    for i in range(len(squares)):
        for j in range(len(squares)):
            for k in range(4):
                square_i = squares[i]
                square_j = squares[j]
                if i == j:
                    continue
                elif i < j:
                    dissimilarity[k][i][j] = difference(square_i, square_j, k)
                else:
                    dissimilarity[k][i][j] = dissimilarity[2 - k][j][i]

    percentiles = np.zeros((4, len(squares)))
    for i in range(len(squares)):
        for k in range(4):
            percentiles[k][i] = np.percentile(np.delete(dissimilarity[k][i], i), 25)

    compatability = np.zeros((4, len(squares), len(squares)))
    for i in range(len(squares)):
        for j in range(len(squares)):
            for k in range(4):
                square_i = squares[i]
                square_j = squares[j]
                if i == j:
                    continue
                elif i < j:
                    compatability[k][i][j] = 0 if percentiles[k][i] == 0 else np.exp(-1 * dissimilarity[k][i][j] / percentiles[k][i]) 
                else:
                    compatability[k][i][j] = compatability[2 - k][j][i]

    best_neighbour = np.zeros((4, len(squares)))
    for k in range(4):
        for i in range(len(squares)):
            best_neighbour[k][i] = np.argmax(compatability[k][i])
    
    answer = np.zeros((rows, cols), dtype = int) - 1
    remaining = set(range(rows * cols))
    answer[rows // 2][cols // 2] = 0
    remaining.remove(0)

    max_score = -1

    while True:
        answer = place(answer, compatability, best_neighbour, remaining, squares)
        score = calculate_score(answer, best_neighbour)
        print(score)
        if score <= max_score:
            break

        max_score = score

        segments = segment(answer, best_neighbour)
        max_segment = largest_segment(answer, segments)

        show_image(max_segment, squares, M, N)
        
        non_zero_row, non_zero_col = np.nonzero(max_segment + 1)
        delta_y = rows // 2 - (max(non_zero_row) + min(non_zero_row)) // 2 - 1 
        delta_x = cols // 2 - (max(non_zero_col) + min(non_zero_col)) // 2 - 1
        max_segment = np.roll(max_segment, delta_y, 0)
        max_segment = np.roll(max_segment, delta_x, 1)
        remaining = set(max_segment[max_segment != -1])
        remaining = set(range(rows * cols)) - remaining
        answer = max_segment

        show_image(answer, squares, M, N)

    show_image(answer, squares, M, N)

def largest_segment(answer, segments):
    indices, count = np.unique(segments, return_counts=True)
    return np.where(segments == indices[np.argmax(count)], answer, -1)

def segment(answer, best):
    M, N = answer.shape
    segments = np.zeros((M, N), dtype = int)
    segment_counter = 1

    while True:
        unassigned_coords = np.argwhere(segments == 0)
        if unassigned_coords.size == 0:
            break

        stack = [unassigned_coords[np.random.choice(range(len(unassigned_coords)))]]
        while stack:
            i, j = stack.pop()
            segments[i][j] = segment_counter
            for x, y in adjacent(i, j):
                if x >= 0 and x < M and y >= 0 and y < N:
                    if segments[x][y] != 0:
                        continue

                    
                    in_segment = True
                    for k in range(4):
                        a,b = move(k, x, y)
                        if a >= 0 and a < M and b >= 0 and b < N and segments[a][b] == segment_counter:
                            if best[2-k][answer[x][y]] == answer[a][b] and best[k][answer[a][b]] == answer[x][y]:  
                                in_segment = False
                    
                    if in_segment:
                        stack.append((x,y))
        segment_counter += 1
    return segments


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--image", type=str)

    args = parser.parse_args();
    image_name = args.image

    rows = 8
    cols = 8

    solve(image_name, rows, cols)
