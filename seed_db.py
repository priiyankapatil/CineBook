from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import Movie, Theatre, Screen, Seat, Show, User, Review

app = create_app()

POSTER_URLS = {
    'The Matrix': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
    'Inception': 'https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
    'Interstellar': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
    'Toy Story': 'https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg',
    'The Dark Knight': '/static/posters/the_dark_knight.jpg',
    'Pulp Fiction': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
    'Parasite': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
    'Spirited Away': 'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg',
    'The Shawshank Redemption': '/static/posters/the_shawshank_redemption.jpg',
    'Fight Club': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
    'Forrest Gump': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
    'The Lord of the Rings: The Return of the King': 'https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg',
    'Goodfellas': '/static/posters/goodfellas.jpg',
    'Gladiator': '/static/posters/gladiator.png',
    'The Silence of the Lambs': '/static/posters/the_silence_of_the_lambs.jpg',
    "Schindler's List": 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg',
    'Whiplash': 'https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg',
    'The Grand Budapest Hotel': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',
    'Coco': '/static/posters/coco.jpg',
    'Joker': '/static/posters/joker.jpg',
    'Avengers: Endgame': 'https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
    'Django Unchained': 'https://image.tmdb.org/t/p/w500/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg',
    'The Lion King': '/static/posters/the_lion_king.jpg',
    'Your Name': '/static/posters/your_name.png',
    'Mad Max: Fury Road': '/static/posters/mad_max_fury_road.jpg',
    'The Social Network': '/static/posters/the_social_network.png',
    'La La Land': '/static/posters/la_la_land.png',
    'Get Out': '/static/posters/get_out.png',
    '3 Idiots': '/static/posters/3_idiots.jpg',
    'PK': '/static/posters/pk.jpg',
    'Baahubali 2: The Conclusion': '/static/posters/baahubali_2_the_conclusion.jpg',
    'RRR': '/static/posters/rrr.jpg',
    'Dangal': '/static/posters/dangal.jpg',
}

SAMPLE_MOVIES = [
    {'title': 'The Matrix', 'description': 'A computer hacker learns about the true nature of reality and his role in the war against its controllers. Neo discovers that his world is a simulation created by intelligent machines.', 'genre': 'Sci-Fi, Action', 'duration_minutes': 136, 'release_date': datetime(1999, 3, 31), 'director': 'Lana Wachowski, Lilly Wachowski', 'language': 'English', 'mlens_movie_id': 1},
    {'title': 'Inception', 'description': 'A skilled thief who steals corporate secrets through dream-sharing technology is given the impossible task of planting an idea into a target\'s subconscious.', 'genre': 'Sci-Fi, Thriller', 'duration_minutes': 148, 'release_date': datetime(2010, 7, 16), 'director': 'Christopher Nolan', 'language': 'English', 'mlens_movie_id': 2},
    {'title': 'Interstellar', 'description': 'When Earth becomes uninhabitable, a team of explorers travels through a wormhole in space to find a new home for humanity among the stars.', 'genre': 'Sci-Fi, Drama', 'duration_minutes': 169, 'release_date': datetime(2014, 11, 7), 'director': 'Christopher Nolan', 'language': 'English', 'mlens_movie_id': 3},
    {'title': 'Toy Story', 'description': 'A cowboy doll is profoundly threatened and jealous when a new spaceman action figure supplants him as top toy in a boy\'s bedroom.', 'genre': 'Animation, Comedy', 'duration_minutes': 81, 'release_date': datetime(1995, 11, 22), 'director': 'John Lasseter', 'language': 'English', 'mlens_movie_id': 4},
    {'title': 'The Dark Knight', 'description': 'When the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological and physical tests to fight injustice.', 'genre': 'Action, Crime, Drama', 'duration_minutes': 152, 'release_date': datetime(2008, 7, 18), 'director': 'Christopher Nolan', 'language': 'English', 'mlens_movie_id': 5},
    {'title': 'Pulp Fiction', 'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption in Los Angeles.', 'genre': 'Crime, Drama', 'duration_minutes': 154, 'release_date': datetime(1994, 10, 14), 'director': 'Quentin Tarantino', 'language': 'English', 'mlens_movie_id': 6},
    {'title': 'Parasite', 'description': 'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.', 'genre': 'Drama, Thriller', 'duration_minutes': 132, 'release_date': datetime(2019, 5, 30), 'director': 'Bong Joon-ho', 'language': 'Korean', 'mlens_movie_id': 7},
    {'title': 'Spirited Away', 'description': 'During her family\'s move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches and spirits.', 'genre': 'Animation, Fantasy', 'duration_minutes': 125, 'release_date': datetime(2001, 7, 20), 'director': 'Hayao Miyazaki', 'language': 'Japanese', 'mlens_movie_id': 8},
    {'title': 'The Shawshank Redemption', 'description': 'Over the course of several years, two convicts form a friendship, seeking consolation and eventual redemption through basic compassion.', 'genre': 'Drama', 'duration_minutes': 142, 'release_date': datetime(1994, 9, 23), 'director': 'Frank Darabont', 'language': 'English', 'mlens_movie_id': 9},
    {'title': 'Fight Club', 'description': 'An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.', 'genre': 'Drama, Thriller', 'duration_minutes': 139, 'release_date': datetime(1999, 10, 15), 'director': 'David Fincher', 'language': 'English', 'mlens_movie_id': 10},
    {'title': 'Forrest Gump', 'description': 'The presidencies of Kennedy and Johnson, the Vietnam War, and more unfold through the perspective of an Alabama man with an IQ of 75.', 'genre': 'Drama, Romance', 'duration_minutes': 142, 'release_date': datetime(1994, 7, 6), 'director': 'Robert Zemeckis', 'language': 'English', 'mlens_movie_id': 11},
    {'title': 'The Lord of the Rings: The Return of the King', 'description': 'Gandalf and Aragorn lead the World of Men against Sauron\'s army to draw his gaze from Frodo and Sam as they approach Mount Doom.', 'genre': 'Adventure, Fantasy', 'duration_minutes': 201, 'release_date': datetime(2003, 12, 17), 'director': 'Peter Jackson', 'language': 'English', 'mlens_movie_id': 12},
    {'title': 'Goodfellas', 'description': 'The story of Henry Hill and his life in the mob, covering his relationship with his wife and his mob partners.', 'genre': 'Crime, Drama', 'duration_minutes': 146, 'release_date': datetime(1990, 9, 13), 'director': 'Martin Scorsese', 'language': 'English', 'mlens_movie_id': 13},
    {'title': 'Gladiator', 'description': 'A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.', 'genre': 'Action, Drama', 'duration_minutes': 155, 'release_date': datetime(2000, 5, 5), 'director': 'Ridley Scott', 'language': 'English', 'mlens_movie_id': 14},
    {'title': 'The Silence of the Lambs', 'description': 'A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer to catch another serial killer.', 'genre': 'Crime, Thriller', 'duration_minutes': 118, 'release_date': datetime(1991, 2, 14), 'director': 'Jonathan Demme', 'language': 'English', 'mlens_movie_id': 15},
    {'title': 'Schindler\'s List', 'description': 'In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.', 'genre': 'Drama, History', 'duration_minutes': 195, 'release_date': datetime(1993, 12, 15), 'director': 'Steven Spielberg', 'language': 'English', 'mlens_movie_id': 16},
    {'title': 'Whiplash', 'description': 'A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing.', 'genre': 'Drama, Music', 'duration_minutes': 106, 'release_date': datetime(2014, 10, 10), 'director': 'Damien Chazelle', 'language': 'English', 'mlens_movie_id': 17},
    {'title': 'The Grand Budapest Hotel', 'description': 'A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy.', 'genre': 'Comedy, Adventure', 'duration_minutes': 99, 'release_date': datetime(2014, 3, 28), 'director': 'Wes Anderson', 'language': 'English', 'mlens_movie_id': 18},
    {'title': 'Coco', 'description': 'Aspiring musician Miguel enters the Land of the Dead to find his great-great-grandfather, a legendary singer.', 'genre': 'Animation, Adventure', 'duration_minutes': 105, 'release_date': datetime(2017, 11, 22), 'director': 'Lee Unkrich', 'language': 'English', 'mlens_movie_id': 19},
    {'title': 'Joker', 'description': 'In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution.', 'genre': 'Crime, Drama', 'duration_minutes': 122, 'release_date': datetime(2019, 10, 4), 'director': 'Todd Phillips', 'language': 'English', 'mlens_movie_id': 20},
    {'title': 'Avengers: Endgame', 'description': 'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos\' actions and restore balance to the universe.', 'genre': 'Action, Adventure', 'duration_minutes': 181, 'release_date': datetime(2019, 4, 26), 'director': 'Anthony Russo, Joe Russo', 'language': 'English', 'mlens_movie_id': 21},
    {'title': 'Django Unchained', 'description': 'With the help of a German bounty-hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.', 'genre': 'Western, Drama', 'duration_minutes': 165, 'release_date': datetime(2012, 12, 25), 'director': 'Quentin Tarantino', 'language': 'English', 'mlens_movie_id': 22},
    {'title': 'The Lion King', 'description': 'Lion prince Simba flees his kingdom after the murder of his father, but returns as an adult to reclaim his throne from his uncle.', 'genre': 'Animation, Drama', 'duration_minutes': 88, 'release_date': datetime(1994, 6, 24), 'director': 'Roger Allers, Rob Minkoff', 'language': 'English', 'mlens_movie_id': 23},
    {'title': 'Your Name', 'description': 'Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?', 'genre': 'Animation, Romance', 'duration_minutes': 106, 'release_date': datetime(2016, 8, 26), 'director': 'Makoto Shinkai', 'language': 'Japanese', 'mlens_movie_id': 24},
    {'title': 'Mad Max: Fury Road', 'description': 'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners.', 'genre': 'Action, Sci-Fi', 'duration_minutes': 120, 'release_date': datetime(2015, 5, 15), 'director': 'George Miller', 'language': 'English', 'mlens_movie_id': 25},
    {'title': 'The Social Network', 'description': 'As Harvard student Mark Zuckerberg creates the social networking site that would become Facebook, he is sued by the twins who claimed he stole their idea.', 'genre': 'Drama, Biography', 'duration_minutes': 120, 'release_date': datetime(2010, 10, 1), 'director': 'David Fincher', 'language': 'English', 'mlens_movie_id': 26},
    {'title': 'La La Land', 'description': 'While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations.', 'genre': 'Romance, Music', 'duration_minutes': 128, 'release_date': datetime(2016, 12, 9), 'director': 'Damien Chazelle', 'language': 'English', 'mlens_movie_id': 27},
    {'title': 'Get Out', 'description': 'A young African-American visits his white girlfriend\'s parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.', 'genre': 'Horror, Thriller', 'duration_minutes': 104, 'release_date': datetime(2017, 2, 24), 'director': 'Jordan Peele', 'language': 'English', 'mlens_movie_id': 28},
    {'title': '3 Idiots', 'description': 'Two friends embark on a quest for a lost buddy. On this journey, they encounter a long forgotten bet, a wedding they must crash, and a funeral that goes impossibly wrong.', 'genre': 'Comedy, Drama', 'duration_minutes': 170, 'release_date': datetime(2009, 12, 25), 'director': 'Rajkumar Hirani', 'language': 'Hindi', 'mlens_movie_id': 29},
    {'title': 'PK', 'description': 'An alien on Earth loses the only device he can use to communicate with his spaceship. His innocent mind helps him to question the religious beliefs around him.', 'genre': 'Comedy, Sci-Fi', 'duration_minutes': 153, 'release_date': datetime(2014, 12, 19), 'director': 'Rajkumar Hirani', 'language': 'Hindi', 'mlens_movie_id': 30},
    {'title': 'Baahubali 2: The Conclusion', 'description': 'When Shiva, the son of Bahubali, learns about his heritage, he begins to look for answers. His story is juxtaposed with past events that unfolded in the Mahishmati Kingdom.', 'genre': 'Action, Fantasy', 'duration_minutes': 167, 'release_date': datetime(2017, 4, 28), 'director': 'S. S. Rajamouli', 'language': 'Telugu', 'mlens_movie_id': 31},
    {'title': 'RRR', 'description': 'A fearless revolutionary and a British Indian soldier forge an unlikely bond when they set off to rescue a young girl from a perilous fate.', 'genre': 'Action, Drama', 'duration_minutes': 187, 'release_date': datetime(2022, 3, 25), 'director': 'S. S. Rajamouli', 'language': 'Telugu', 'mlens_movie_id': 32},
    {'title': 'Dangal', 'description': 'Former wrestler Mahavir Singh Phogat trains his two daughters to become world-class wrestlers, defying all odds and societal norms.', 'genre': 'Drama, Biography', 'duration_minutes': 161, 'release_date': datetime(2016, 12, 23), 'director': 'Nitesh Tiwari', 'language': 'Hindi', 'mlens_movie_id': 33},
]

THEATRES = [
    {'name': 'PVR INOX', 'location': 'City Centre Mall, Downtown, Mumbai', 'screens': 3},
    {'name': 'Cinepolis', 'location': 'Westside Plaza, Andheri West, Mumbai', 'screens': 2},
    {'name': 'IMAX Wadala', 'location': 'Phoenix Marketcity, Wadala, Mumbai', 'screens': 2},
    {'name': 'Miraj Cinemas', 'location': 'R City Mall, Ghatkopar, Mumbai', 'screens': 2},
    {'name': 'INOX Leisure', 'location': 'Nexus Seawoods, Navi Mumbai', 'screens': 1},
]

SEAT_TYPES = [
    ('A', 1, 10, 'standard', 1.0),
    ('B', 1, 10, 'standard', 1.0),
    ('C', 1, 10, 'standard', 1.0),
    ('D', 1, 10, 'vip', 1.5),
    ('E', 1, 10, 'recliner', 2.0),
]

BASE_PRICES = {
    'standard': 149,
    'vip': 299,
    'recliner': 499,
}


def seed():
    with app.app_context():
        db.create_all()

        if Movie.query.first():
            print('Database already seeded. Skipping.')
            return

        movies = []
        for data in SAMPLE_MOVIES:
            title = data['title']
            poster = POSTER_URLS.get(title)
            movie = Movie(**data, poster_url=poster)
            db.session.add(movie)
            movies.append(movie)

        theatres = []
        for t_data in THEATRES:
            theatre = Theatre(name=t_data['name'], location=t_data['location'],
                              total_screens=t_data['screens'])
            db.session.add(theatre)
            theatres.append(theatre)
        db.session.flush()

        all_screens = []
        for theatre in theatres:
            theatre_data = next(t for t in THEATRES if t['name'] == theatre.name)
            for screen_num in range(1, theatre_data['screens'] + 1):
                screen = Screen(theatre_id=theatre.id, screen_number=screen_num,
                                total_seats=50)
                db.session.add(screen)
                all_screens.append(screen)
        db.session.flush()

        for screen in all_screens:
            for row_char, start, end, stype, mult in SEAT_TYPES:
                for num in range(start, end + 1):
                    seat = Seat(
                        screen_id=screen.id,
                        seat_row=row_char,
                        seat_number=num,
                        seat_type=stype,
                        price_multiplier=mult,
                    )
                    db.session.add(seat)

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for i, movie in enumerate(movies):
            screen = all_screens[i % len(all_screens)]
            for hour in [10, 13, 16, 19, 22]:
                show = Show(
                    movie_id=movie.id,
                    screen_id=screen.id,
                    show_time=today + timedelta(days=1, hours=hour),
                    base_price=BASE_PRICES['standard'],
                )
                db.session.add(show)

        demo_user = User(username='demo', email='demo@example.com')
        demo_user.set_password('password')
        db.session.add(demo_user)

        db.session.commit()
        print(f'Seeded {len(movies)} movies, {len(theatres)} theatres, '
              f'{len(all_screens)} screens with shows for tomorrow.')


if __name__ == '__main__':
    seed()
