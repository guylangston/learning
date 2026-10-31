-- runner.lua: run a shell command and show its output in a bottom split.
--
-- Load:   :source ./runner.lua
-- Use:    :lua quick_run("cat ./alice_in_wonderland.txt | python3 huffman.py --svg")
--         <leader>rr  prompts for a command (pre-filled with the last one)
--         q           closes the output window

local BUF_NAME = "quick_run://output"

local function get_output_buf()
  local buf = vim.fn.bufnr(BUF_NAME)
  if buf == -1 then
    -- unlisted scratch buffer: buftype=nofile, noswapfile
    buf = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_name(buf, BUF_NAME)
    vim.bo[buf].bufhidden = "hide"
    vim.keymap.set("n", "q", "<cmd>close<cr>", { buffer = buf, nowait = true, silent = true })
  end
  return buf
end

local function open_output_win(buf)
  local win = vim.fn.bufwinid(buf)
  if win == -1 then
    vim.cmd("botright 15split")
    win = vim.api.nvim_get_current_win()
    vim.api.nvim_win_set_buf(win, buf)
  else
    vim.api.nvim_set_current_win(win)
  end
  vim.wo[win].number = false
  vim.wo[win].relativenumber = false
  vim.wo[win].signcolumn = "no"
  vim.wo[win].winfixheight = true
  return win
end

function _G.quick_run(cmd)
  vim.g.quick_run_last_cmd = cmd

  -- wrap in a subshell so stderr from every stage of a pipeline is captured
  local output = vim.fn.systemlist("(" .. cmd .. ") 2>&1")
  local exit_code = vim.v.shell_error
  if #output == 0 then
    output = { "(no output)" }
  end

  local buf = get_output_buf()
  vim.bo[buf].readonly = false
  vim.bo[buf].modifiable = true
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, output)
  vim.bo[buf].modifiable = false
  vim.bo[buf].readonly = true
  vim.bo[buf].modified = false

  local win = open_output_win(buf)
  vim.api.nvim_win_set_cursor(win, { 1, 0 })
  -- '%' is special in winbar, so escape it
  vim.wo[win].winbar = ("$ %s  [exit %d]"):format(cmd, exit_code):gsub("%%", "%%%%")
end

vim.keymap.set("n", "<leader>rr", function()
  vim.ui.input(
    { prompt = "Run: ", default = vim.g.quick_run_last_cmd, completion = "shellcmd" },
    function(cmd)
      if cmd and cmd ~= "" then
        quick_run(cmd)
      end
    end
  )
end, { desc = "quick_run: run a shell command" })
