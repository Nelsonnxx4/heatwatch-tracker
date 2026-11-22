from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City

CitySeed = tuple[str, str, str, str, float, float]

NIGERIAN_CITIES: list[CitySeed] = [
    ("abuja", "Abuja", "FCT", "Nigeria", 9.0765, 7.3986),
    ("aba", "Aba", "Abia", "Nigeria", 5.1216, 7.3733),
    ("abeokuta", "Abeokuta", "Ogun", "Nigeria", 7.1475, 3.3619),
    ("akure", "Akure", "Ondo", "Nigeria", 7.2571, 5.2058),
    ("benin-city", "Benin City", "Edo", "Nigeria", 6.3350, 5.6037),
    ("calabar", "Calabar", "Cross River", "Nigeria", 4.9757, 8.3417),
    ("ilorin", "Ilorin", "Kwara", "Nigeria", 8.4966, 4.5421),
    ("jos", "Jos", "Plateau", "Nigeria", 9.8965, 8.8583),
    ("kaduna", "Kaduna", "Kaduna", "Nigeria", 10.5105, 7.4165),
    ("katsina", "Katsina", "Katsina", "Nigeria", 12.9908, 7.6018),
    ("lafia", "Lafia", "Nasarawa", "Nigeria", 8.4939, 8.5153),
    ("lagos", "Lagos", "Lagos", "Nigeria", 6.5244, 3.3792),
    ("lokoja", "Lokoja", "Kogi", "Nigeria", 7.8023, 6.7333),
    ("kano", "Kano", "Kano", "Nigeria", 12.0022, 8.5919),
    ("port-harcourt", "Port Harcourt", "Rivers", "Nigeria", 4.8156, 7.0498),
    ("makurdi", "Makurdi", "Benue", "Nigeria", 7.7337, 8.5214),
    ("maiduguri", "Maiduguri", "Borno", "Nigeria", 11.8333, 13.1500),
    ("enugu", "Enugu", "Enugu", "Nigeria", 6.4584, 7.5464),
    ("ibadan", "Ibadan", "Oyo", "Nigeria", 7.3775, 3.9470),
    ("minna", "Minna", "Niger", "Nigeria", 9.6139, 6.5569),
    ("onitsha", "Onitsha", "Anambra", "Nigeria", 6.1429, 6.7924),
    ("owerri", "Owerri", "Imo", "Nigeria", 5.4891, 7.0176),
    ("sokoto", "Sokoto", "Sokoto", "Nigeria", 13.0059, 5.2476),
    ("uyo", "Uyo", "Akwa Ibom", "Nigeria", 5.0377, 7.9128),
    ("warri", "Warri", "Delta", "Nigeria", 5.5160, 5.7500),
    ("yenagoa", "Yenagoa", "Bayelsa", "Nigeria", 4.9247, 6.2642),
    ("yola", "Yola", "Adamawa", "Nigeria", 9.2035, 12.4954),
    ("zaria", "Zaria", "Kaduna", "Nigeria", 11.0855, 7.7199),
]

US_CITIES: list[CitySeed] = [
    ("new-york", "New York", "New York", "United States", 40.7128, -74.0060),
    ("los-angeles", "Los Angeles", "California", "United States", 34.0522, -118.2437),
    ("chicago", "Chicago", "Illinois", "United States", 41.8781, -87.6298),
    ("houston", "Houston", "Texas", "United States", 29.7604, -95.3698),
    ("phoenix", "Phoenix", "Arizona", "United States", 33.4484, -112.0740),
    ("philadelphia", "Philadelphia", "Pennsylvania", "United States", 39.9526, -75.1652),
    ("san-antonio", "San Antonio", "Texas", "United States", 29.4241, -98.4936),
    ("san-diego", "San Diego", "California", "United States", 32.7157, -117.1611),
    ("dallas", "Dallas", "Texas", "United States", 32.7767, -96.7970),
    ("austin", "Austin", "Texas", "United States", 30.2672, -97.7431),
    ("miami", "Miami", "Florida", "United States", 25.7617, -80.1918),
    ("atlanta", "Atlanta", "Georgia", "United States", 33.7490, -84.3880),
    ("seattle", "Seattle", "Washington", "United States", 47.6062, -122.3321),
    ("boston", "Boston", "Massachusetts", "United States", 42.3601, -71.0589),
    ("denver", "Denver", "Colorado", "United States", 39.7392, -104.9903),
    ("washington-dc", "Washington", "District of Columbia", "United States", 38.9072, -77.0369),
    ("san-francisco", "San Francisco", "California", "United States", 37.7749, -122.4194),
    ("las-vegas", "Las Vegas", "Nevada", "United States", 36.1699, -115.1398),
    ("detroit", "Detroit", "Michigan", "United States", 42.3314, -83.0458),
    ("minneapolis", "Minneapolis", "Minnesota", "United States", 44.9778, -93.2650),
]

EUROPEAN_CITIES: list[CitySeed] = [
    ("london", "London", "England", "United Kingdom", 51.5074, -0.1278),
    ("paris", "Paris", "Île-de-France", "France", 48.8566, 2.3522),
    ("berlin", "Berlin", "Berlin", "Germany", 52.5200, 13.4050),
    ("madrid", "Madrid", "Community of Madrid", "Spain", 40.4168, -3.7038),
    ("rome", "Rome", "Lazio", "Italy", 41.9028, 12.4964),
    ("amsterdam", "Amsterdam", "North Holland", "Netherlands", 52.3676, 4.9041),
    ("brussels", "Brussels", "Brussels-Capital", "Belgium", 50.8503, 4.3517),
    ("vienna", "Vienna", "Vienna", "Austria", 48.2082, 16.3738),
    ("lisbon", "Lisbon", "Lisbon", "Portugal", 38.7223, -9.1393),
    ("dublin", "Dublin", "Leinster", "Ireland", 53.3498, -6.2603),
    ("copenhagen", "Copenhagen", "Capital Region", "Denmark", 55.6761, 12.5683),
    ("stockholm", "Stockholm", "Stockholm County", "Sweden", 59.3293, 18.0686),
    ("oslo", "Oslo", "Oslo", "Norway", 59.9139, 10.7522),
    ("helsinki", "Helsinki", "Uusimaa", "Finland", 60.1699, 24.9384),
    ("warsaw", "Warsaw", "Masovian", "Poland", 52.2297, 21.0122),
    ("prague", "Prague", "Prague", "Czechia", 50.0755, 14.4378),
    ("budapest", "Budapest", "Central Hungary", "Hungary", 47.4979, 19.0402),
    ("athens", "Athens", "Attica", "Greece", 37.9838, 23.7275),
    ("bucharest", "Bucharest", "Bucharest", "Romania", 44.4268, 26.1025),
    ("barcelona", "Barcelona", "Catalonia", "Spain", 41.3874, 2.1686),
    ("milan", "Milan", "Lombardy", "Italy", 45.4642, 9.1900),
    ("munich", "Munich", "Bavaria", "Germany", 48.1351, 11.5820),
    ("zurich", "Zurich", "Zürich", "Switzerland", 47.3769, 8.5417),
    ("geneva", "Geneva", "Geneva", "Switzerland", 46.2044, 6.1432),
    ("istanbul", "Istanbul", "Istanbul", "Türkiye", 41.0082, 28.9784),
    ("edinburgh", "Edinburgh", "Scotland", "United Kingdom", 55.9533, -3.1883),
    ("kyiv", "Kyiv", "Kyiv", "Ukraine", 50.4501, 30.5234),
]

OTHER_GLOBAL_CITIES: list[CitySeed] = [
    ("toronto", "Toronto", "Ontario", "Canada", 43.6532, -79.3832),
    ("vancouver", "Vancouver", "British Columbia", "Canada", 49.2827, -123.1207),
    ("montreal", "Montreal", "Quebec", "Canada", 45.5019, -73.5674),
    ("mexico-city", "Mexico City", "Mexico City", "Mexico", 19.4326, -99.1332),
    ("sao-paulo", "São Paulo", "São Paulo", "Brazil", -23.5505, -46.6333),
    ("buenos-aires", "Buenos Aires", "Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("cairo", "Cairo", "Cairo", "Egypt", 30.0444, 31.2357),
    ("nairobi", "Nairobi", "Nairobi County", "Kenya", -1.2921, 36.8219),
    ("johannesburg", "Johannesburg", "Gauteng", "South Africa", -26.2041, 28.0473),
    ("dubai", "Dubai", "Dubai", "United Arab Emirates", 25.2048, 55.2708),
    ("mumbai", "Mumbai", "Maharashtra", "India", 19.0760, 72.8777),
    ("delhi", "Delhi", "Delhi", "India", 28.6139, 77.2090),
    ("singapore", "Singapore", "Singapore", "Singapore", 1.3521, 103.8198),
    ("tokyo", "Tokyo", "Tokyo", "Japan", 35.6762, 139.6503),
    ("seoul", "Seoul", "Seoul", "South Korea", 37.5665, 126.9780),
    ("sydney", "Sydney", "New South Wales", "Australia", -33.8688, 151.2093),
    ("melbourne", "Melbourne", "Victoria", "Australia", -37.8136, 144.9631),
]

CITIES = [
    *NIGERIAN_CITIES,
    *US_CITIES,
    *EUROPEAN_CITIES,
    *OTHER_GLOBAL_CITIES,
]


async def seed_cities(session: AsyncSession) -> int:
    existing = {
        city.slug: city for city in (await session.scalars(select(City))).all()
    }
    new = []
    for slug, name, state, country, lat, lon in CITIES:
        city = existing.get(slug)
        if city is None:
            new.append(
                City(
                    slug=slug,
                    name=name,
                    state=state,
                    country=country,
                    latitude=lat,
                    longitude=lon,
                )
            )
            continue
        city.name = name
        city.state = state
        city.country = country
        city.latitude = lat
        city.longitude = lon

    session.add_all(new)
    await session.commit()
    return len(new)
