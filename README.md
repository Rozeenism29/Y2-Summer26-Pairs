# Y2-Summer26-Pair-Project
# Objective

During Labs 1-3, each of you built an AI agent using the Claude API. Your agent could complete a task through the terminal, but it worked independently and had no graphical interface.

By the end of Lab 6, your team should have a working multi-agent application with a fully functional backend and a frontend built using Bolt.

# Requirements

Your finished project should include:

- **One AI agent per team member.** Teams of two should build two collaborating agents. Teams of three should build three.
- **A clear responsibility for each agent.** Every agent should contribute something different to the overall product.
- **A deliverable for the user.** The user should receive something useful—not just text. Examples include a study plan, checklist, report, travel plan, exported document, or another useful result.
- **One working tool call.** a python function, e.g.: export to PDF/text, save a file, search past results, or generate a calendar-style output.
- **Relevant responses.** Your agents should react to the user's input and to information received from the other agents. Avoid generic responses that could fit every conversation.
- **Functional User Interface.** Your app has a well designed user interface created by Bolt.

## Milestone 1 — Design Before You Build

Before writing new code, design your product as a team.

Decide:

- What is the main idea of the web app?
- What responsibility does each agent have?
- How does the user move through the application from beginning to end?
- What is the final product?

**Next, get your idea approved by your instructors**

## Milestone 2 — System Prompts

Build a strong and precise System Prompt for each agent

Your system prompt should answer the following statements:

- WHO the agent is (name and role)
- WHAT it does (specific task)
- WHAT IT WILL NOT DO (clear boundaries)

> 💡 **Remember, Agents have a role and a goal.**

Update the system prompt so every response uses this exact format:

- [Summary]: one sentence repeating what the user asked
- [Response]: the main answer
- [Next Step]: one concrete action the user can take

## Milestone 3 — Build the Backend

Now begin implementing your complete backend, each agent on a different python file, you should have: app1.py and app2.py

By the end of this milestone, your team should have:

- every agent working independently
- all required tool calls functioning (python function that produces
- the complete workflow running successfully from the terminal

Do **not** use Bolt yet.

At this stage, everything should work without a graphical interface.

**Test: send a few messages and confirm the agent stays in role, follows the format, and gives a better answer on a hard question.**

Your file structure should look like this:

![](https://raw.githubusercontent.com/meet-projects/Y2-Summer26-Pairs/refs/heads/main/backend.png
)
### ✅ Backend Checklist

Before moving on, make sure every statement below is true.

- [ ] Every agent works correctly by itself.
- [ ] Every agent has a clear responsibility.
- [ ] Tool calls work reliably.
- [ ] The complete workflow runs from start to finish in the terminal.
- [ ] Every team member understands how the backend works.

Only after completing this checklist should you continue.

## Milestone 4 — Connect your agents together

In this milestone, you'll bring both agents into one app. Instead of running app1.py and app2.py separately, the user picks which agent they want to use when they run the program.

What this means: you write one new file (like main.py) that starts by asking the user a question, like:

"Which agent do you want to use?

1. Agent 1 — [does X]
2. Agent 2 — [does Y]"

Based on what the user picks, main.py calls that agent's function and runs it.

Steps:

- Turn each agent into a callable function. Instead of running app1.py and app2.py on their own, each file should have one function like run_agent(input) that returns a result. main.py will import both.
- Write the selection menu. In main.py, ask the user which agent they want (by number or name), and use their answer to decide which function to call.
- Run only the chosen agent. Once the user picks, main.py should call that agent's function, pass along whatever input it needs, and show the result — the other agent should not run.
- Make sure both options actually work. Test picking Agent 1, then restart and test picking Agent 2. Each should complete its task and produce a result on its own.
- Handle a bad input. If the user types something that isn't a valid option, the app should ask again instead of crashing.

> 💡 **Remember Test each agent through the menu one at a time. Confirm Agent 1 works through main.py before testing Agent 2.**

Your file structure should look like this:

![](https://raw.githubusercontent.com/meet-projects/Y2-Summer26-Pairs/refs/heads/main/combined-back.png
)

### Connection Checklist

- [ ] Running main.py shows a clear menu asking which agent to use.
- [ ] Picking Agent 1 runs only Agent 1 and gives a correct result.
- [ ] Picking Agent 2 runs only Agent 2 and gives a correct result.
- [ ] Invalid input doesn't crash the app.
- [ ] Both partners understand how main.py picks and runs the chosen agent.

Once every box is checked, you're ready to move on to agent collaboration.

## Milestone 5 — Agent Collaboration

So far your agents have run independently — the user picks one, it runs, and it returns a result. Now make them actually work together.

Instead of treating each agent as an idependant option, make them collborate.

What this means:

- Run Agent 1 first and capture its output (don't just print it and discard it — store it in a variable).
- Ask the user for an additional input once Agent 1 has finished.
- Pass both Agent 1's output and the new user input into Agent 2.
- Agent 2 should build its response using both pieces of information, not just the new input alone.
- Optional: maintain a combined history across both agents, so Agent 2 (and any later step) has context on what Agent 1 already did, not just its final output in isolation.

Steps:

- Update Agent 2's function so it accepts an extra parameter (Agent 1's output) in addition to the user's new input.
- In main.py, call Agent 1's function, save the result, then call Agent 2's function with both that result and the new user input.
- If you added the history option: keep a running history object or list that both agents can read from, so the final output reflects the full conversation, not just the last message.
- Test that Agent 2's response actually changes depending on what Agent 1 produced — this confirms real collaboration rather than two disconnected agents.


### Collaboration Checklist

- [ ] Agent 1's output is captured and stored, not just printed.
- [ ] The user is prompted for a new input after Agent 1 runs.
- [ ] Agent 2 receives both Agent 1's output and the new user input.
- [ ] Agent 2's final result clearly reflects information from Agent 1.
- [ ] Combined history is maintained and used, not discarded between agents.

Once every box is checked, you're ready to build the replit frontend.

## Milestone 6 — Building the face

Now it's time to turn your working backend into a real app using [Replit Agent](https://replit.com/)

Write one detailed prompt for Replit that explains:

- What each agent does (its specific job)
- How you want the app to look and feel
- That each agent needs its own tab, with a different chat page for each agent — it's important to mention this explicitly, otherwise Replit may merge both agents into one chat.

To connect your code to the frontend:
- Make sure your code is pushed into github
- Copy your project link: click on the code button which will give you the option to copy the project link
- In Replit, click on "Import to Replit" --> "Import from GitHub"--> add the link.(if you are still confused refer back to the slides to know how to add it)

Copy this and include it in your prompts:

"Update the Anthropic client initialization to read the base URL from the environment: `new Anthropic({ apiKey, baseURL: process.env.ANTHROPIC_BASE_URL })`. Then add `ANTHROPIC_API_KEY=your-key-here` and `ANTHROPIC_BASE_URL=your-base-url` to the environment variables."

Send your prompt and let the Replit agent build!

> 💡 Remember
> Remember what we talked about in our previous sessions about clarity, feedback, and focus? Make sure to keep those in mind when prompting!


## Milestone 7 — Connect a Database with Supabase

Now that your app works end to end, give it persistence by connecting it to a Supabase database.

What this means: instead of losing all results and history when the app restarts, your data (agent outputs, user inputs, combined history, etc.) gets saved to and read from a real database.

Steps:

- Create a Supabase project and connect it to your app that the Replit Agent created - for more detailed instructions refer back to the slides.

### Database Checklist

- [ ] Supabase project and tables are created.
- [ ] Backend successfully writes data to Supabase.
- [ ] Backend successfully reads data back from Supabase.
- [ ] Data still exists after restarting the app.

## Milestone 8 — Test and Improve

Test your complete application like a real user.

Try different inputs, including unexpected ones.

When you find a problem, fix one issue at a time and test again.

Continue improving your prompts, backend, and frontend until the entire system works reliably.

Once you reach this stage, deploy your web app: click on the publish button in Replit Agent so your project goes live!

