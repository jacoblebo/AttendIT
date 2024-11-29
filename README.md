# AttendIT

## Project Overview
Over the course of our undergraduate experience, we’ve found that attendance isn’t always the easiest to keep track of, especially in classes with hundreds of students. We’ve also found that each instructor seems to handle attendance somewhat differently, with some using daily quizzes, while others resort to verbally asking each student, one-by-one, if they’re present during class. A question arises, is there a way to create a better, more efficient attendance system that’s easy to learn and easy to use?
This is the primary goal of our attendance app project. 
After successful completion of the app, the task of taking attendance would become a mostly hands-off experience. Additionally, instructors would be able to easily track attendance metrics across time, and students would have access to reliable feedback and suggestions regarding their attendance habits.


### Setup Instructions
  - Open Git bash
  - git clone https://github.com/jacoblebo/AttendIT
  - Navigate to the project directory using the cd command
  - Start a virtual environment
    - Linux/MacOS:
      - python -m venv .venv
      - source venv/bin/activate
    - Windows:
      - Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
      - python -m venv .venv
      - .\venv\Scripts\Activate
  - Install requirements.txt files
    - pip install -r requirements.txt
  - Create SECRET_KEY .env variable
    - This can be any string.
    - Create a file called .env
    - Make the contents of the file this line:
      - SECRET_KEY = '1DDE168B0DC710D629E3AA2C1F0ABA39'
  - Start the application: flask run
### Usage Details
  - User can login  with mobile device or desktop to confirm attendance
  - Instructor can automatically compile attendance
  - The current instructor account has the following credentials:
    - Username: admin@uncc.edu
    - Password: 123
 - The default student account has the following credentials:
   - Username: test@uncc.edu
   - Password: 123
 - You CANNOT create another professor account, that action can only be preformed by a DBA. This design decision was made so that we didn't need to worry about figuring out who was a professor or not. Assumedly, if this platform gets adoption, we can request a list of emails and then run an Update-Select statement.

### Team Progress
  - Created Wireframe
  - Set Up Flask Web Application

