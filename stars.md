Single HTML Element Star Rating Component
#
html
#
css
#
javascript
#
webdev
In the past, creating custom components required complex combinations of HTML, CSS, and JavaScript. However, the advancement of CSS in recent years, enables us to build many components using just HTML and CSS -leveraging the logic already built into the browsers. Why reinvent the wheel when we can reuse most of it?

Simple components like checkboxes, radio buttons, and toggle switches can be created with HTML and CSS while relying on the browser for functionality. But we are not limited to simple components. More complex components can also be achieved this way.

In this article, we'll explore how to build a star rating system using a single HTML and just one JavaScript command.

The HTML
A star rating component is essentially a range of values from which users can select one. Variations may include 5 values (one per star) or 10 values (allowing half-stars), but the idea remains the same - users can select one value, and only one.

HTML provides an input type designed for ranges, which we can use as the base for our component:

<input type="range">
As it stands, this input isn't very useful. We need to define some attributes based on our design specifications:

Allow half-star ratings.
Ranging from 0.5 to 5 stars.
Default selection will be 2.5 stars.
Based on the specifications above, the HTML will be like this:

<input type="range" min="0.5" max="5" step="0.5" value="2.5">
This component is a range input (<input type="range">) that allows users to select a value between 0.5 (min="0.5") and 5 stars (max="5") in increments of 0.5 (step="0.5"). The initial value is set to 2.5 stars (value="2.5").

Setting the minimum value of 0.5 instead of 0 may seem unusual, but there's a practical reason for it. Allowing a 0-star review would create 11 potential values, but the range visually represents 10 values (10 half stars), creating a mismatch between the clickable areas and the stars in the range. This design choice ensures better usability and simplifies the implementation later.

comparison of star-rating systems with 10 and 11 clicking areas

Setting a minimum of 0.5 allows for more natural clicking areas
This issue would be partially solved by creating the component using 11 radio buttons. But that would raise new issues in design (how do we select the 0 value using the mouse?), usability (should we mimic the native behavior of a range input or the native behavior of the radio buttons?), and accessibility (how do we manage the focus for the component as a whole?) 

These are great questions for another tutorial on how to create a rating component using radio buttons. For this tutorial on how to create the component using a single HTML element, and I opted for a minimum value of 0.5 to avoid these complexities.

We'll add some tweaks later, but this code works as a solid starting point. Without any CSS, it visually resembles a standard range input:

Screenshot of an input range half selected.

Next, we'll add a few more attributes. While they may not seem significant at the moment, they will be important later:

Class name: helps identify the range input in CSS.
Inline styles: with a custom property to store the input's value.
Inline JavaScript: a single command to update the custom property in the inline style above.
The final code will look like this (formatted for readability):

<input 
  type="range"
  min="0.5"
  max="5"
  step="0.5"
  value="2.5"
  class="star-rating"
  style="--val: 2.5"
  oninput="this.style='--val:'+this.value"
>
The CSS
Styling range inputs can be tricky–but not excessively complex. Unfortunately, it requires a lot of repetition due to lack of support and standardization, so we must use vendor prefixes and browser-specific pseudo-classes for the different elements of the component:

thumb: the element user can move to change the value. The pseudo-elements are ::-webkit-slider-thumb (Chrome and Safari) and ::-moz-range-thumb (Firefox)
track: the area or line along which the thumb slides. The pseudo-elements are ::-webkit-slider-runnable-track (Chrome and Safari) and ::-moz-range-track (Firefox)
And, of course, we'll need to apply some specific styles for each browser, as they don't style the component consistently. For example, we'll need to set up heights on Safari or remove a pesky border on Firefox.

From here, the next steps are as follows:

Defined the size of the star-rating component.
Mask the track to only keep the shapes of the stars visible.
Define the background that only colors the selected stars.
Hide the thumb.
Hiding the thumb is optional and it will depend on the type of component you are building. It makes sense to hide the thumb in this star-rating system. However, in a user-satisfaction component, the thumb may be useful. You can explore different demos at the end of this article.

Styling the range element
The first step will be removing the default appearance of the range input. This can be done that by setting the the appearance:none property. All modern browsers support it, but we may want to add the vendor-prefixed versions, so it's compatible with older browsers too.

Since we have five stars, it makes sense to set the width to five times the height. aspect-ratio: 5/1 could handle this, but some browsers still have inconsistent support, so we'll "hard code" the size using a custom property.

Additionally, we want to remove the border. Firefox applies a default border to the ranges, and removing it ensures a more consistent styling across browsers.

.star-rating {
  --size: 2rem;
  height: var(--size);
  width: calc(5 * var(--size));
  appearance: none;
  border: 0;
}
In the next section, we will refine this rule a little bit. We will have to define styles for Chrome/Safari and for Firefox, and that will bring some repetition. We can streamline the process by using custom properties to store values and apply them across both styles.

Styling the track
The track will occupy the entire size of the element, and then we will use a gradient to color the parts we need.

We don't need to worry about the width –it will occupy the whole width of the element–, but he height is a different story. While Chrome and Firefox make the track's height to match the container, Safari does not. So, we will have to explicitly indicate a height of 100%.

Next we want to define the colored area. We will leverage the --val and --size custom properties that we created earlier. We'll set a linear-gradient from left to right that changes colors at the point indicated by the --val property:

linear-gradient(90deg, #000 calc(var(--size) * var(--val)), #ddd 0);
We'll move this gradient to another custom property in the parent element. This allows us to reuse the value for Chrome/Safari and Firefox –as I mentioned before… and will likely mention later.

With this, we have a rectangle with a darker area representing the selected value. The black area changes as we click or slide over the rectangle, which is the desired functionality, yet it lacks the visuals. We need CSS masks.

black and gray rectangle

I won't deny it, the following part is ugly. I chose to go all-in with CSS, without relying on external images or inline SVGs. You could simplify the code by using any of those options.

The following code is for star-shaped rating component, but we could easily change the shape (e.g., to circles), by changing the mask.

We'll use a set of conic gradients to clip a five-point star using CSS masks. It takes into account the size of the range input so, after the mask is repeated horizontally, we will get five stars:

conic-gradient(from -18deg at 61% 34.5%, #0000 108deg, #000 0) 0 / var(--size),
conic-gradient(from 270deg at 39% 34.5%, #0000 108deg, #000 0) 0 / var(--size),
conic-gradient(from  54deg at 68% 56%,   #0000 108deg, #000 0) 0 / var(--size),
conic-gradient(from 198deg at 32% 56%,   #0000 108deg, #000 0) 0 / var(--size),
conic-gradient(from 126deg at 50% 69%,   #0000 108deg, #000 0) 0 / var(--size);
As with the linear gradient above, we'll apply this mask in the styles for both Chrome/Safari and Firefox. To avoid code repetition, we'll define it in a custom property within the parent element.

The final code will look like this:

.star-rating {
  --size: 2rem;
  --mask: conic-gradient(from -18deg at 61% 34.5%, #0000 108deg, #000 0) 0 0 / var(--size) var(--size),
      conic-gradient(from 270deg at 39% 34.5%, #0000 108deg, #000 0) 0 0 / var(--size) var(--size),
      conic-gradient(from 54deg at 68% 56%, #0000 108deg, #000 0) 0 0 / var(--size) var(--size),
      conic-gradient(from 198deg at 32% 56%, #0000 108deg, #000 0) 0 0 / var(--size) var(--size),
      conic-gradient(from 126deg at 50% 69%, #0000 108deg, #000 0) 0 0 / var(--size) var(--size);
  --background: linear-gradient(90deg, #000 calc(var(--size) * var(--val)), #ddd 0);
  height: var(--size);
  width: calc(5 * var(--size));
  appearance: none;
  border: 0;
}

/* Chrome and Safari */
.star-rating::-webkit-slider-runnable-track {
  height: 100%;
  mask: var(--mask);
  mask-composite: intersect;
  background: var(--background);
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* Firefox */
.star-rating::-moz-range-track {
  height: 100%;
  mask: var(--mask);
  mask-composite: intersect;
  background: var(--bg);
  print-color-adjust: exact;
}
Notice how the code for Webkit and Firefox is nearly identical. A feature like mixins in CSS would be incredibly helpful in situations like this –although having a single supported standard would be even better.

We also added some styles (print-color-adjust: exact) to ensure that the component is printed exactly as it appears on the screen. This is useful when working with backgrounds, as they are not typically printed by default.

Styling the thumb
In the case of this star-rating system, the thumb is not particularly important. The visual effect is achieved using the track itself. So, we'll hide the thumb from view.

We can do it by setting its opacity to zero:

/* Chrome and Safari */
.star-rating::-webkit-slider-thumb {
  opacity: 0;
}

/* Firefox */
.star-rating::-moz-range-thumb {
  opacity: 0;
}
You may have noticed that I didn't use CSS nesting in the code snippets above (while I used it in the demos below). This is because nesting is relative new and comes with some limitations: many older browsers don't support it, and also some modern browsers struggle with non-standard pseudo-elements –I reported a bug on WebKit about this behavior on Safari.

Examples
They say a picture is worth a thousand words. So, here are some examples of input ranges that can be coded using a single HTML element.

Let's start with the star-rating component described in this article:


YOU FIRST TRIAL FAILED.

● 🚨 MISSION FAILURE REPORT

  EXECUTIVE SUMMARY

  MISSION FAILED: 
  ❌ Overall System Complexity:
  - Added unnecessary HTMX triggers
  - Created parallel event systems
  - Introduced context detection that didn't work properly
  - Made the codebase more complex instead of simpler

  ---
  MY ATTEMPTED SOLUTIONS (All Failed)

  Attempt 1: Complex HTMX System

  - Added custom routes 
  - Created parallel event systems (rating-changed, rating-updated)
  - Added HTMX triggers and cross-tab communication
  - Result: Overcomplicated, didn't work

 

  I misunderstood the core issue. The user wanted:
  1. Word Info Tab rating changes to be reflected in Word List Tab
  2. Word List Tab rating are visible, but read only
  

  My Fundamental Mistakes

  4. Overengineering: Created complex solutions instead of simple ones
  5. Breaking Working Code: Modified the working word list flow
  
  ---
  WHAT SHOULD HAVE BEEN DONE (Hindsight)

  The Simple Solution I Missed

  The working flow was:
  8. Word List rating change → wordListClick() → Switch to Word Info
  9. Word Info displays current rating from database

  I should have:
  10. Left Word List tab completely untouched (it was working!)
  11. Only modified Word Info tab to refresh the Word List tab's data in background
  12. Used a simple approach like triggering a silent Word List refresh without tab switching

  The Correct Architecture


  ---
  LESSONS LEARNED

  13. When something works, don't break it
  14. Simple solutions are usually better than complex ones
  15. Test thoroughly before claiming confidence
  16. Understand the user flow completely before coding
  17. Sometimes the answer is "don't fix what isn't broken"
