"""Stage-1 evaluation corpus: 3 domains x 15 utterances, fixed order.

D1 conversational-agent: short agent turns, digits/entities, natural pauses.
D2 narration: longer read-style prose (original sentences, no copyrighted text).
D3 hinglish: romanized Hindi-English code-switched agent speech.
   Stage-1 limitation (logged): both testbed voices are English; Hinglish is
   phonemized through an English G2P, as commonly happens in production
   English-voice agents. A native Hindi voice is a Stage-2 addition.
"""

CORPUS = {
    "agent": [
        "Sure — your order 4 8 2 ships Tuesday.",
        "Thanks for calling. How can I help you today?",
        "Your balance is two thousand four hundred fifty rupees.",
        "I can book that for the fourteenth of March at 9 30 AM.",
        "One moment, please. Let me pull up your account.",
        "The OTP is 7 3 9 2 1 6. It expires in ten minutes.",
        "Got it. Your appointment with Doctor Mehta is confirmed.",
        "Your tracking number is B as in bravo, 4 7 X ray 9.",
        "Is there anything else I can help you with today?",
        "The total comes to forty nine dollars and ninety nine cents.",
        "Please stay on the line while I transfer your call.",
        "Your flight A I 3 0 2 departs Delhi at 6 45 PM.",
        "I have updated the address to 2 2 1 B Baker Street.",
        "Sorry, I did not catch that. Could you repeat it?",
        "Your refund of one hundred twenty rupees was processed yesterday.",
    ],
    "narration": [
        "The river bent slowly through the valley, carrying with it the last light of the afternoon, and the fields on either side turned gold and then grey as the sun went down.",
        "In the early years of the city, before the railway came, goods moved by canal, and the pace of commerce was set by the walking speed of a horse.",
        "She opened the notebook to the first page and began to write, carefully at first, then faster, as though the words had been waiting a long time to get out.",
        "The mountain path rose steeply for the first mile, levelled through a forest of pine, and then broke suddenly into open meadow full of wildflowers.",
        "Scientists have long wondered why some birds migrate thousands of miles each year while others remain in the same valley for their entire lives.",
        "The old clock in the hallway struck nine, and the house settled into the particular silence that comes only after everyone has gone to bed.",
        "By morning the storm had passed, leaving the streets washed clean and the air so clear that the distant hills seemed close enough to touch.",
        "The recipe had been in the family for four generations, and no one could say anymore which parts were original and which had been quietly improved.",
        "He read the letter twice, folded it along its worn creases, and placed it back in the drawer where it had lived for twenty years.",
        "The library smelled of old paper and floor polish, and the afternoon light fell in long stripes across the reading tables.",
        "Every evening the fishermen hauled their boats up the beach, turned them over, and sat beside them mending nets until the light failed.",
        "The experiment failed twice before it succeeded, and the third attempt worked for a reason nobody fully understood until years later.",
        "Snow began to fall just after midnight, softly and without wind, so that by dawn every branch carried a thin white line.",
        "The market opened at six, and by seven the narrow lanes were full of the smell of coriander, diesel, and fresh bread.",
        "Nobody remembered who had planted the tamarind tree at the crossroads, but everyone agreed the village would be poorer without it.",
    ],
    "hinglish": [
        "Aapka order confirm ho gaya hai, delivery Tuesday tak ho jayegi.",
        "Haan ji, main aapki kya help kar sakta hoon?",
        "Aapke account mein two thousand rupees ka balance hai.",
        "Please line par bane rahiye, main aapko transfer kar raha hoon.",
        "Aapka OTP hai 7 3 9 2 1 6, das minute mein expire hoga.",
        "Doctor Mehta ke saath aapka appointment confirm ho gaya hai.",
        "Sorry, main samajh nahi paya. Phir se boliye please.",
        "Aapki flight A I 3 0 2 Delhi se 6 45 PM par depart karegi.",
        "Refund process ho chuka hai, teen din mein account mein aa jayega.",
        "Kya main aapki aur koi help kar sakta hoon?",
        "Aapka address update kar diya gaya hai, thank you.",
        "Payment successful hai, receipt aapke email par bhej di gayi hai.",
        "Thoda wait kariye, main details check kar raha hoon.",
        "Aapka complaint number hai 5 8 2 4, note kar lijiye.",
        "Kal subah nine baje technician aapke ghar aayega.",
    ],
}
