1. Develop an E/R model for the database described above, start by finding suitable entity sets. Hint: We will not need any entity set for the company itself.

2. Find relationships between the entity sets. Indicate the multiplicities of all relationships.

3. Find attributes of the entity sets and (possibly) of the relationships.

4. Identify keys, both primary keys and foreign keys. Answer these questions (put your answer in lab2-answers.md):

a. Which relations have natural keys?

   -- All tables except for tickets (ticket_id) have natural keys.

b. Is there a risk that any of the natural keys will ever change?

   -- customer (user_name), theaters (theather_name) might be changed.

c. Are there any weak entity sets?

   -- performances is weak.

d. In which relations do you want to use an invented key. Why?

   -- When there is no obvious natural key that can be used. For example for defining the key for a ticket as we did with default(..randomblob..)

5. Draw a UML diagram of your E/R model, using some program – it should be as clear and tidy as possible, and it must follow the standard for UML class diagrams. Make sure to have the file with your model available for the lab session.

6. Convert the E/R model to a relational model, use the method described during lecture 4.

Describe your model in your lab2-answers.md file – use the following conventions:

underscores for primary keys
slashes for foreign keys
underscores and slashes for attributes which are both (parts of) primary keys and foreign keys
--
   theaters(_theater_name_, capacity)
   movies(_imdb_key_, movie_name, running_time)
   performances(/_theater_name_/, /_imdb_key_/, start_time)
   customers(_username_, first_name, last_name, password, /ticket_id/)
   tickets(_ticket_id_, /theater_name/, /imdb_key/)
--
For the college application example we had during lecture 2 we would end up with:
   students(s_id, s_name, gpa, size_hs)
   colleges(c_name, state, enrollment)
   applications(/_s_id_/, /_c_name_/, major, decision)

7. There are at least two ways of keeping track of the number of seats available for each performance – describe them both, with their upsides and downsides (write your answer in lab2-answers.md).

-- 7.1 Add a list of tickets in performances that holds all the tickets (seats) that are assigned to it.
-- 7.2 Every ticket has a foreign key of a movie and a theater, so we can easily get the number of seats booked for each performances.

For your own database, you can choose either method, but you should definitely be aware of both.