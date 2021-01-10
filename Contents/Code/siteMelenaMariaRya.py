import PAsearchSites
import PAgenres
import PAactors
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    sceneID = searchTitle.split(' ', 1)[0]
    try:
        sceneTitle = searchTitle.split(' ', 1)[1]
    except:
        sceneTitle = ''

    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    titleNoFormatting = detailsPageElements.xpath('//title')[0].text_content().split(' - Sex Movies Featuring Melena Maria Rya')[0]
    titleNoFormatting = re.sub(r'[^A-Za-z0-9\s\-]+', ' ', titleNoFormatting).strip()

    curID = PAutils.Encode(sceneURL)
    releaseDate = searchDate if searchDate else ''

    score = 100

    results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [MelenaMariaRya]' % titleNoFormatting, score=score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')

    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL

    sceneDate = None
    if len(metadata_id) > 2:
        sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().split(' - Sex Movies Featuring Melena Maria Rya')[0]
    metadata.title = re.sub('[^A-Za-z0-9\s\-]', ' ', metadata.title).strip()
    metadata.title = re.sub(r' with ([A-Z][a-z]+) ([A-Z][a-z]+)', '', metadata.title)

    # Summary
    metadata.summary = detailsPageElements.xpath('//meta[@name="description"]/@content')[0].strip()

    # Studio
    metadata.studio = 'MelenaMariaRya'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre('European')

    # Actors
    movieActors.clearActors()
    movieActors.addActor('Melena Maria Rya', '')

    m = re.search(r' with ([A-Z][a-z]+ [A-Z][a-z]+)', metadata.title)
    if m:
        movieActors.addActor(m.group(1), '')

    # Posters/Background
    art = []
    xpaths = []
    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if (width > 1 or height > width) and width < height:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata